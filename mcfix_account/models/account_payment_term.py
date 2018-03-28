from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res.append(self.env['account.invoice'].search(
            [('payment_term_id', '=', self.id)]))
        return res
