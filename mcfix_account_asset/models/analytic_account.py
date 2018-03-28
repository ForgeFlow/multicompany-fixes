from odoo import models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.asset.category',
             [('account_analytic_id', '=', self.id)]),
        ]
        return res
