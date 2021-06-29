from odoo import api, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.depends("company_id")
    def name_get(self):
        names = super(PickingType, self).name_get()
        res = self.add_company_suffix(names)
        return res


class Picking(models.Model):
    _inherit = "stock.picking"
    _check_company_auto = True

    @api.onchange("picking_type_id", "partner_id")
    def onchange_picking_type(self):
        super(Picking, self).onchange_picking_type()
        if self.picking_type_id:
            self.company_id = self.picking_type_id.company_id.id

    @api.model
    def create(self, vals):
        defaults_pick_type = self.default_get(["picking_type_id"]).get(
            "picking_type_id"
        )
        if not vals.get("company_id"):
            vals["company_id"] = (
                self.env["stock.picking.type"]
                .browse(vals.get("picking_type_id", defaults_pick_type))
                .company_id.id
            )
        return super(Picking, self).create(vals)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.backorder_id:
            if not self.picking_type_id.check_company(self.company_id):
                self.picking_type_id = self.env["stock.picking.type"].search(
                    [
                        ("code", "=", self.picking_type_id.code),
                        ("warehouse_id.company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not self.picking_type_id:
                    self.picking_type_id = self.env["stock.picking.type"].search(
                        [
                            ("code", "=", self.picking_type_id.code),
                            ("warehouse_id", "=", False),
                        ],
                        limit=1,
                    )
            if not self.partner_id.check_company(self.company_id):
                self.partner_id = False
            if not self.location_id.check_company(self.company_id):
                self.location_id = False
            if not self.location_dest_id.check_company(self.company_id):
                self.location_dest_id = False
            if not self.owner_id.check_company(self.company_id):
                self.owner_id = False
            if self.company_id and self.move_lines:
                for line in self.move_lines:
                    if line.check_company(self.company_id):
                        line.company_id = self.company_id

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.move_lines,
            self.move_line_ids,
        ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ("stock.picking", [("backorder_id", "=", self.id)]),
            ("stock.scrap", [("picking_id", "=", self.id)]),
        ]
        return res
