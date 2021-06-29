from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_ids = fields.One2many(check_company=True)

    @api.model
    def _default_warehouse_id(self):
        # This method can be removed when
        # https://github.com/odoo/odoo/pull/24063 is merged.
        super(SaleOrder, self)._default_warehouse_id()
        company = self.env.context.get("company_id") or self.env.company.id
        warehouse_ids = self.env["stock.warehouse"].search(
            [("company_id", "=", company)], limit=1
        )
        return warehouse_ids

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        if not self.warehouse_id.check_company(self.company_id):
            self.set_warehouse()

    def set_warehouse(self):
        self.warehouse_id = self.with_context(
            company_id=self.company_id.id
        )._default_warehouse_id()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    move_ids = fields.One2many(check_company=True)
