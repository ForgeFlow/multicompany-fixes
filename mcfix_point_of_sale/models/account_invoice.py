from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.order', [('invoice_id', '=', self.id)]),
        ]
        return res
