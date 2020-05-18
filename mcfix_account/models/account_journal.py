from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountJournalGroup(models.Model):
    _inherit = 'account.journal.group'
    _check_company_auto = True

    excluded_journal_ids = fields.Many2many(check_company=True)


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _check_company_auto = True

    account_control_ids = fields.Many2many(check_company=True)
    default_credit_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=True)
    default_debit_account_id = fields.Many2one(check_company=True)
    profit_account_id = fields.Many2one(check_company=True)
    loss_account_id = fields.Many2one(check_company=True)
    bank_account_id = fields.Many2one(check_company=True)
    journal_group_ids = fields.Many2many(check_company=True)
    secure_sequence_id = fields.Many2one(check_company=True)

    def get_journal_dashboard_datas(self):
        return super(AccountJournal, self.sudo()).get_journal_dashboard_datas()

    def action_open_reconcile(self):
        if self.type in ['bank', 'cash']:
            if len(self.mapped('company_id').ids) > 1:
                raise UserError(
                    _('All journals should be of the same company.'))
        return super(AccountJournal, self).action_open_reconcile()

    @api.depends('company_id')
    def name_get(self):
        names = super(AccountJournal, self).name_get()
        res = self.add_company_suffix(names)
        return res
    #
    # @api.depends('company_id')
    # def _compute_belong_to_company_or_child(self):
    #     for journal in self:
    #         journal.belong_to_company_or_child = len(self.search(
    #             [('company_id', 'child_of', self.env.user.company_id.id)])) > 0
    #
    # def _search_user_company_and_child_journals(self, operator, value):
    #     companies = self.env.user.company_id
    #     companies += self.env.user.company_id.child_ids
    #     if operator == '=':
    #         recs = self.search([('company_id', 'in', companies.ids)])
    #     elif operator == '!=':
    #         recs = self.search([('company_id', 'not in', companies.ids)])
    #     else:
    #         raise UserError(_("Invalid search operator."))
    #
    #     return [('id', 'in', [x.id for x in recs])]
    #
    # belong_to_company_or_child = fields.Boolean(
    #     'Belong to the user\'s current child company',
    #     compute="_compute_belong_to_company_or_child",
    #     search="_search_user_company_and_child_journals")

    def write(self, vals):
        for journal in self:
            if vals.get('company_id'):
                sequence_id = vals.get('sequence_id', journal.sequence_id.id)
                sequence = self.env['ir.sequence'].browse(sequence_id)
                if sequence and sequence.company_id.id != vals['company_id']:
                    sequence.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
                refund_sequence_id = vals.get('refund_sequence_id',
                                              journal.refund_sequence_id.id)
                refund_sequence = self.env[
                    'ir.sequence'].browse(refund_sequence_id)
                if refund_sequence and refund_sequence.company_id.id != vals[
                    'company_id'
                ]:
                    refund_sequence.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
                if vals.get('type', journal.type) in ('bank', 'cash'):
                    default_debit_account_id = vals.get(
                        'default_debit_account_id',
                        journal.default_debit_account_id.id)
                    default_debit_account = self.env[
                        'account.account'].browse(default_debit_account_id)
                    if default_debit_account and \
                            default_debit_account.company_id.id != vals[
                            'company_id']:
                        default_debit_account.with_context(
                            bypass_company_validation=True).write(
                            {'company_id': vals['company_id']})
                    default_credit_account_id = vals.get(
                        'default_credit_account_id',
                        journal.default_credit_account_id.id)
                    default_credit_account = self.env[
                        'account.account'].browse(default_credit_account_id)
                    if default_credit_account and \
                            default_credit_account.company_id.id != vals[
                            'company_id']:
                        default_credit_account_id.with_context(
                            bypass_company_validation=True).write(
                            {'company_id': vals['company_id']})
                    bank_account_id = vals.get(
                        'bank_account_id',
                        journal.bank_account_id.id)
                    bank_account = self.env[
                        'res.partner.bank'].browse(bank_account_id)
                    if bank_account and bank_account.company_id.id != vals[
                            'company_id']:
                        company = self.env['res.company'].browse(
                            vals['company_id'])
                        bank_account.with_context(
                            bypass_company_validation=True).write(
                            {'company_id': company.id,
                             'partner_id': company.partner_id.id})
        return super(AccountJournal, self).write(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.profit_account_id.check_company(self.company_id):
            self.profit_account_id = False
        if not self.loss_account_id.check_company(self.company_id):
            self.loss_account_id = False
        if not self.account_control_ids.check_company(self.company_id):
            self.account_control_ids = self.account_control_ids.filtered(
                lambda a: a.company_id == self.company_id or not a.company_id)
        if not self.default_debit_account_id.check_company(self.company_id):
            self.default_debit_account_id.company_id = self.company_id
        if not self.default_credit_account_id.check_company(self.company_id):
            self.default_credit_account_id.company_id = self.company_id
        if not self.sequence_id.check_company(self.company_id):
            self.sequence_id.company_id = self.company_id

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.bank.statement', [('journal_id', '=', self.id)]),
            ('account.bank.statement.line', [('journal_id', '=', self.id)]),
            ('account.move', [('journal_id', '=', self.id)]),
            ('account.move.line', [('journal_id', '=', self.id)]),
            ('account.payment', [('destination_journal_id', '=', self.id)]),
            ('account.payment', [('journal_id', '=', self.id)]),
            ('account.reconcile.model', [('journal_id', '=', self.id)]),
            ('account.reconcile.model', [('second_journal_id', '=', self.id)]),
        ]
        return res
