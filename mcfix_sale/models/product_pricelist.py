from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order", [("pricelist_id", "=", self.id)]),
        ]
        return res
