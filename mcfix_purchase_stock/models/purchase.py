from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    picking_ids = fields.Many2many(check_company=True)
    picking_type_id = fields.Many2one(check_company=True)

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        super(PurchaseOrder, self)._onchange_picking_type_id()
        if self.picking_type_id and not self.env.context.get("no_change_company"):
            self.company_id = self.picking_type_id.warehouse_id.company_id.id

    def set_picking_type(self):
        self.picking_type_id = self.with_context(
            company_id=self.company_id.id
        )._default_picking_type()

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.picking_type_id.check_company(self.company_id):
            self.set_picking_type()
        super(PurchaseOrder, self)._onchange_company_id()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    orderpoint_id = fields.Many2one(check_company=True)
    move_ids = fields.One2many(check_company=True)
    move_dest_ids = fields.One2many(check_company=True)
