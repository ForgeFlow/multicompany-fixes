# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  inverse_name='journal_id', string='Invoices')

    @api.multi
    @api.depends('company_id')
    def _belong_to_company_or_child(self):
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
        compute="_belong_to_company_or_child",
        search="_search_user_company_and_child_journals")

    @api.multi
    @api.depends('name', 'currency_id', 'company_id', 'company_id.currency_id')
    def name_get(self):
        res = []
        journal_names = super(AccountJournal, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return journal_names
        for journal_name in journal_names:
            journal = self.browse(journal_name[0])
            name = "%s [%s]" % (journal_name[1], journal.company_id.name)
            res += [(journal.id, name)]
        return res

    @api.multi
    @api.constrains('default_credit_account_id', 'company_id')
    def _check_company_credit_account_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.default_credit_account_id and\
                    journal.company_id != journal.default_credit_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Credit Account must be the same.'))
        return True

    @api.multi
    @api.constrains('default_debit_account_id', 'company_id')
    def _check_company_debit_account_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.default_debit_account_id and\
                    journal.company_id != journal.default_debit_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Debit Account must be the same.'))
        return True

    @api.multi
    @api.constrains('account_control_ids', 'company_id')
    def _check_company_account_control_ids(self):
        for journal in self.sudo():
            for account in journal.account_control_ids:
                if journal.company_id and \
                                journal.company_id != account.company_id:
                    raise ValidationError(
                        _('The Company in the Journal and in Accounts Allowed '
                          'must be the same.'))
        return True

    @api.multi
    @api.constrains('profit_account_id', 'company_id')
    def _check_company_profit_account_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.profit_account_id and\
                    journal.company_id != journal.profit_account_id.company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Profit Account must be the same.'))
        return True

    @api.multi
    @api.constrains('loss_account_id', 'company_id')
    def _check_company_loss_account_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.loss_account_id and\
                    journal.company_id != journal.loss_account_id.company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Loss Account must be the same.'))
        return True

    @api.multi
    @api.constrains('bank_account_id', 'company_id')
    def _check_company_bank_account_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.bank_account_id and\
                    journal.company_id != journal.bank_account_id.company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'the Bank Account must be the same.'))
        return True

    @api.multi
    @api.constrains('sequence_id', 'company_id')
    def _check_company_sequence_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.sequence_id and\
                    journal.company_id != journal.sequence_id.company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'the Sequence must be the same.'))
        return True

    @api.multi
    @api.constrains('refund_sequence_id', 'company_id')
    def _check_company_refund_sequence_id(self):
        for journal in self.sudo():
            if journal.company_id and journal.refund_sequence_id and\
                    journal.company_id != journal.refund_sequence_id.company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'the Refund Sequence must be the '
                                        'same.'))
        return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.account_control_ids = False
        self.profit_account_id = False
        self.loss_account_id = False

    def write(self, vals):
        if 'company_id' in vals:
            if self.env['account.move'].search(
                    [('journal_id', 'in', self.ids)], limit=1):
                raise ValidationError(_(
                    'This journal already contains items, therefore '
                    'you cannot modify its company.'))
            if self.env['account.invoice'].search(
                    [('journal_id', 'in', self.ids)], limit=1):
                raise ValidationError(_(
                    'This journal already contains invoices, therefore '
                    'you cannot modify its company.'))

        for journal in self:
            if 'company_id' in vals:
                if (
                    journal.sequence_id and
                    journal.sequence_id.company_id.id != vals['company_id']
                ):
                    journal.sequence_id.write(
                        {'company_id': vals['company_id']})
                elif (
                    journal.refund_sequence_id and
                    journal.refund_sequence_id.company_id.id != vals[
                                'company_id']
                ):
                    journal.refund_sequence_id.write(
                        {'company_id': vals['company_id']})
                if (
                    journal.default_debit_account_id and
                    journal.default_debit_account_id.company_id.id != vals[
                                'company_id']
                ):
                    if self.env['account.move.line'].search(
                            [('account_id', '=',
                              journal.default_debit_account_id.id)], limit=1):
                        raise ValidationError(_(
                            'Account %s already contains items, therefore '
                            'you cannot modify its company.'
                            % journal.default_debit_account_id.code))

                    journal.default_debit_account_id.write(
                        {'company_id': vals['company_id']})

                if (
                    journal.default_credit_account_id and
                    journal.default_credit_account_id.company_id.id != vals[
                                'company_id']
                ):
                    if self.env['account.move.line'].search(
                            [('account_id', '=',
                              journal.default_credit_account_id.id)], limit=1):
                        raise ValidationError(_(
                            'Account %s already contains items, therefore '
                            'you cannot modify its company.'
                            % journal.default_credit_account_id.code))
                    journal.default_credit_account_id.write({
                        'company_id': vals['company_id']})

                if (
                    journal.bank_account_id and
                    journal.bank_account_id.company_id.id != vals[
                                'company_id']
                ):
                    company = self.env['res.company'].browse(vals['company_id'])
                    journal.bank_account_id.write({
                        'company_id': company.id,
                        'partner_id': company.partner_id.id})

        return super(AccountJournal, self).write(vals)
