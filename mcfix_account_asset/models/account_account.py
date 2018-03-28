from odoo import models


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.asset.category',
             [('account_depreciation_id', '=', self.id)]),
            ('account.asset.category', [('account_asset_id', '=', self.id)]),
            ('account.asset.category',
             [('account_depreciation_expense_id', '=', self.id)]),
        ]
        return res
