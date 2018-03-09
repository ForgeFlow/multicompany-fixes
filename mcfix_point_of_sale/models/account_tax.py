from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.order.line', [('tax_ids', 'in', self.ids)]),
        ]
        return res
