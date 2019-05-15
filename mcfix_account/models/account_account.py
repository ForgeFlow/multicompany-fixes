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
        if not self.tax_ids.check_company(self.company_id):
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
        res += [self.tax_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.analytic.line', [('general_account_id', '=', self.id)]),
            ('account.bank.statement.line', [('account_id', '=', self.id)]),
            ('account.invoice', [('account_id', '=', self.id)]),
            ('account.invoice.line', [('account_id', '=', self.id)]),
            ('account.invoice.tax', [('account_id', '=', self.id)]),
            ('account.journal', [('profit_account_id', '=', self.id)]),
            ('account.journal', [('default_debit_account_id', '=', self.id)]),
            ('account.journal', [('loss_account_id', '=', self.id)]),
            ('account.journal', [('default_credit_account_id', '=', self.id)]),
            ('account.journal', [('account_control_ids', 'in', self.ids)]),
            ('account.move.line', [('account_id', '=', self.id)]),
            ('account.payment', [('writeoff_account_id', '=', self.id)]),
            ('account.reconcile.model', [('account_id', '=', self.id)]),
            ('account.reconcile.model', [('second_account_id', '=', self.id)]),
            ('account.tax', [('account_id', '=', self.id)]),
            ('account.tax', [('cash_basis_account_id', '=', self.id)]),
            ('account.tax', [('refund_account_id', '=', self.id)]),
        ]
        return res
