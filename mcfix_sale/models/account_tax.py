from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order.line', [('tax_id', 'in', self.ids)]),
        ]
        return res
