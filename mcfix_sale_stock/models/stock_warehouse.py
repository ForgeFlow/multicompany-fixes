from odoo import models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order", [("warehouse_id", "=", self.id)]),
        ]
        return res
