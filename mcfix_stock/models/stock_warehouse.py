from odoo import api, fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    crossdock_route_id = fields.Many2one(check_company=True)
    reception_route_id = fields.Many2one(check_company=True)
    delivery_route_id = fields.Many2one(check_company=True)
    resupply_wh_ids = fields.Many2many(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.name:
            self.name = self.company_id.name
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = self.company_id.partner_id
        if not self.resupply_wh_ids.check_company(self.company_id):
            self.resupply_wh_ids = self.env["stock.warehouse"].search(
                [
                    ("resupply_wh_ids", "in", [self.id]),
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ]
            )
        if not self.route_ids.check_company(self.company_id):
            self.route_ids = self.env["stock.location.route"].search(
                [
                    ("warehouse_selectable", "=", True),
                    ("warehouse_ids", "in", [self.id]),
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ]
            )
        # if not self.wh_input_stock_loc_id.check_company(self.company_id):
        #     self.wh_input_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_input_stock_loc_id
        # if not self.crossdock_route_id.check_company(self.company_id):
        #     self.crossdock_route_id = self.default_resupply_wh_id.\
        #         crossdock_route_id
        # if not self.wh_qc_stock_loc_id.check_company(self.company_id):
        #     self.wh_qc_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_qc_stock_loc_id
        # if not self.reception_route_id.check_company(self.company_id):
        #     self.reception_route_id = self.default_resupply_wh_id.\
        #         reception_route_id
        # if not self.mto_pull_id.check_company(self.company_id):
        #     self.mto_pull_id = self.default_resupply_wh_id.mto_pull_id
        # if not self.view_location_id.check_company(self.company_id):
        #     self.view_location_id = self.default_resupply_wh_id.\
        #         view_location_id
        # if not self.wh_output_stock_loc_id.check_company(self.company_id):
        #     self.wh_output_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_output_stock_loc_id
        # if not self.lot_stock_id.check_company(self.company_id):
        #     self.lot_stock_id = self.default_resupply_wh_id.lot_stock_id
        # if not self.wh_pack_stock_loc_id.check_company(self.company_id)::
        #     self.wh_pack_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_pack_stock_loc_id
        # if not self.delivery_route_id.check_company(self.company_id):
        #     self.delivery_route_id = self.default_resupply_wh_id.\
        #         delivery_route_id

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.route_ids, self.resupply_route_ids, self.resupply_wh_ids]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ("stock.rule", [("propagate_warehouse_id", "=", self.id)]),
            ("stock.rule", [("warehouse_id", "=", self.id)]),
            ("stock.location.route", [("warehouse_ids", "in", self.ids)]),
            ("stock.move", [("warehouse_id", "=", self.id)]),
            ("stock.picking.type", [("warehouse_id", "=", self.id)]),
            ("stock.warehouse", [("resupply_wh_ids", "in", self.ids)]),
            ("stock.warehouse.orderpoint", [("warehouse_id", "=", self.id)]),
        ]
        return res


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.product_id.check_company(self.company_id):
            self.product_id = False
        if not self.warehouse_id.check_company(self.company_id):
            self.warehouse_id = self.product_id.warehouse_id
        if not self.location_id.check_company(self.company_id):
            self.location_id = self.product_id.location_id
