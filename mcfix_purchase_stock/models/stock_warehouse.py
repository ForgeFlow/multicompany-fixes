from odoo import fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    buy_pull_id = fields.Many2one(check_company=True)

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     super(Warehouse, self)._onchange_company_id()
    #     if not self.buy_pull_id.check_company(self.company_id):
    #         self.buy_pull_id = self.default_resupply_wh_id.buy_pull_id


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order.line', [('orderpoint_id', '=', self.id)]),
        ]
        return res
