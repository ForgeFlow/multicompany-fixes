from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"
    _check_company_auto = True

    @api.depends('company_id')
    def name_get(self):
        names = super(AccountAccount, self).name_get()
        res = self.add_company_suffix(names)
        return res

    tax_ids = fields.Many2many(check_company=True)

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
            ('account.journal', [('profit_account_id', '=', self.id)]),
            ('account.journal', [('default_debit_account_id', '=', self.id)]),
            ('account.journal', [('loss_account_id', '=', self.id)]),
            ('account.journal', [('default_credit_account_id', '=', self.id)]),
            ('account.journal', [('account_control_ids', 'in', self.ids)]),
            ('account.move.line', [('account_id', '=', self.id)]),
            ('account.payment', [('writeoff_account_id', '=', self.id)]),
            ('account.reconcile.model', [('account_id', '=', self.id)]),
            ('account.reconcile.model', [('second_account_id', '=', self.id)]),
            ('account.tax', [('cash_basis_base_account_id', '=', self.id)]),
            ('account.tax.repartition.line', [('account_id', '=', self.id)]),
        ]
        return res
