from odoo import models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order", [("payment_term_id", "=", self.id)]),
        ]
        return res
