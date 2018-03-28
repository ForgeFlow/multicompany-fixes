from odoo import api, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.invoice', [('payment_term_id', '=', self.id)]),
        ]
        return res
