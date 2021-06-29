from odoo import fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    buy_pull_id = fields.Many2one(check_company=True)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("purchase.order.line", [("orderpoint_id", "=", self.id)]),
        ]
        return res
