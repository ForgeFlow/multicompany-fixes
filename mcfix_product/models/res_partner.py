from odoo import models


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('product.supplierinfo', [('name', '=', self.id)]),
        ]
        return res
