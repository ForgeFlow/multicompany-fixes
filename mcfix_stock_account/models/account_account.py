from odoo import models


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ("stock.location", [("valuation_in_account_id", "=", self.id)]),
            ("stock.location", [("valuation_out_account_id", "=", self.id)]),
        ]
        return res
