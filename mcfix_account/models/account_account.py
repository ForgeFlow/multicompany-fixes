from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountAccount, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.tax_ids:
            self.tax_ids = self.env['account.tax'].search(
                [('account_id', '=', self.id),
                 ('company_id', '=', False),
                 ('company_id', '=', self.company_id.id)])

    @api.multi
    @api.constrains('company_id', 'tax_ids')
    def _check_company_id_tax_ids(self):
        for rec in self.sudo():
            for line in rec.tax_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Account and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res = res + [
            self.env['account.invoice.line'].search(
                [('account_id', '=', self.id)]),
            self.env['account.analytic.line'].search(
                [('general_account_id', '=', self.id)]),
            self.env['account.move.line'].search(
                [('account_id', '=', self.id)]),
            self.env['account.tax'].search(
                [('cash_basis_account', '=', self.id)]),
            self.env['account.tax'].search(
                [('refund_account_id', '=', self.id)]),
            self.env['account.tax'].search(
                [('account_id', '=', self.id)]),
            self.env['account.payment'].search(
                [('writeoff_account_id', '=', self.id)]),
            self.env['account.invoice'].search(
                [('account_id', '=', self.id)]),
            self.env['account.invoice.tax'].search(
                [('account_id', '=', self.id)]),
            self.env['account.journal'].search(
                [('account_control_ids', 'in', [self.id])]),
            self.env['account.journal'].search(
                [('profit_account_id', 'in', [self.id])]),
            self.env['account.journal'].search(
                [('loss_account_id', 'in', [self.id])]),
            self.env['account.journal'].search(
                [('default_credit_account_id', 'in', [self.id])]),
            self.env['account.journal'].search(
                [('default_debit_account_id', 'in', [self.id])]),
            self.env['account.reconcile.model'].search(
                [('second_account_id', '=', self.id)]),
            self.env['account.reconcile.model'].search(
                [('account_id', '=', self.id)]),
            self.env['account.bank.statement.line'].search(
                [('account_id', '=', self.id)]),
        ]
        return res
