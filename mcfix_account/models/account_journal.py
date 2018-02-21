from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    company_partner_id = fields.Many2one(
        'res.partner', related='company_id.partner_id',
        string='Account Holder', readonly=True)
    bank_account_id = fields.Many2one(
        domain="[('partner_id','=', company_partner_id)]")

    @api.multi
    def get_journal_dashboard_datas(self):
        return super(AccountJournal, self.sudo()).get_journal_dashboard_datas()

    @api.multi
    def action_open_reconcile(self):
        if self.type in ['bank', 'cash']:
            if len(self.mapped('company_id').ids) > 1:
                raise UserError(
                    _('All journals should be of the same company.'))
        return super(AccountJournal, self).action_open_reconcile()

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountJournal, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    @api.depends('company_id')
    def _compute_belong_to_company_or_child(self):
        for journal in self:
            journal.belong_to_company_or_child = len(self.search(
                [('company_id', 'child_of', self.env.user.company_id.id)])) > 0

    @api.multi
    def _search_user_company_and_child_journals(self, operator, value):
        companies = self.env.user.company_id + \
            self.env.user.company_id.child_ids
        if operator == '=':
            recs = self.search([('company_id', 'in', companies.ids)])
        elif operator == '!=':
            recs = self.search([('company_id', 'not in', companies.ids)])
        else:
            raise UserError(_("Invalid search operator."))

        return [('id', 'in', [x.id for x in recs])]

    belong_to_company_or_child = fields.Boolean(
        'Belong to the user\'s current child company',
        compute="_compute_belong_to_company_or_child",
        search="_search_user_company_and_child_journals")

    @api.multi
    def write(self, vals):
        for journal in self:
            if vals.get('company_id'):
                if journal.sequence_id.company_id.id != vals['company_id']:
                    journal.sequence_id.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
                elif journal.refund_sequence_id.company_id.id != vals[
                        'company_id']:
                    journal.refund_sequence_id.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
                if journal.default_debit_account_id.company_id.id != vals[
                        'company_id']:
                    journal.default_debit_account_id.with_context(
                        bypass_company_validation=True).write(
                        {'company_id': vals['company_id']})
                if journal.default_credit_account_id.company_id.id != vals[
                        'company_id']:
                    journal.default_credit_account_id.with_context(
                        bypass_company_validation=True).write(
                        {'company_id': vals['company_id']})
                if journal.bank_account_id.company_id.id != vals[
                        'company_id']:
                    company = self.env['res.company'].browse(
                        vals['company_id'])
                    journal.bank_account_id.with_context(
                        bypass_company_validation=True).write(
                        {'company_id': company.id,
                         'partner_id': company.partner_id.id})
        return super(AccountJournal, self).write(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.profit_account_id.company_id and \
                self.profit_account_id.company_id != self.company_id:
            self.profit_account_id = False
        if self.company_id and self.loss_account_id.company_id and \
                self.loss_account_id.company_id != self.company_id:
            self.loss_account_id = False
        if self.company_id and self.default_debit_account_id.company_id and \
                self.default_debit_account_id.company_id != self.company_id:
            self.default_debit_account_id = False
            # self.default_debit_account_id.company_id = self.company_id
        if self.company_id and self.default_credit_account_id.company_id and \
                self.default_credit_account_id.company_id != self.company_id:
            self.default_credit_account_id = False
            # self.default_credit_account_id.company_id = self.company_id
        if self.company_id and self.account_control_ids:
            self.account_control_ids = self.account_control_ids.filtered(
                lambda a: a.company_id == self.company_id or not a.company_id)

    @api.multi
    @api.constrains('company_id', 'loss_account_id')
    def _check_company_id_loss_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.loss_account_id.company_id and\
                    rec.company_id != rec.loss_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'default_debit_account_id')
    def _check_company_id_default_debit_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.default_debit_account_id.company_id and\
                    rec.company_id != rec.default_debit_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'sequence_id')
    def _check_company_id_sequence_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.sequence_id.company_id and\
                    rec.company_id != rec.sequence_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Ir Sequence must be the same.'))

    @api.multi
    @api.constrains('company_id', 'refund_sequence_id')
    def _check_company_id_refund_sequence_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.refund_sequence_id.company_id and\
                    rec.company_id != rec.refund_sequence_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Ir Sequence must be the same.'))

    @api.multi
    @api.constrains('company_id', 'profit_account_id')
    def _check_company_id_profit_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.profit_account_id.company_id and\
                    rec.company_id != rec.profit_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_control_ids')
    def _check_company_id_account_control_ids(self):
        for rec in self.sudo():
            for line in rec.account_control_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Journal and in '
                          'Account Account (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'default_credit_account_id')
    def _check_company_id_default_credit_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.default_credit_account_id.company_id and\
                    rec.company_id != rec.default_credit_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'bank_account_id')
    def _check_company_id_bank_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.bank_account_id.company_id and\
                    rec.company_id != rec.bank_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Res Partner Bank must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.bank.statement.line'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to '
                          'Account Bank Statement Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.move'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to Account Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('second_journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to '
                          'Account Reconcile Model (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to '
                          'Account Reconcile Model (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.bank.statement'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to '
                          'Account Bank Statement (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.payment'].search(
                    [('destination_journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to Account Payment '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.payment'].search(
                    [('journal_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Journal is assigned to Account Payment '
                          '(%s).' % field.name_get()[0][1]))
