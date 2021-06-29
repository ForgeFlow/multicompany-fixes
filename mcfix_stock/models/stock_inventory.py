from odoo import api, fields, models


class Inventory(models.Model):
    _inherit = "stock.inventory"
    _check_company_auto = True

    location_ids = fields.Many2many(check_company=True)

    @api.model
    def create(self, vals):
        if vals.get("location_ids") and not vals.get("company_id"):
            locations = vals.get("location_ids")
            location_ids = False
            if isinstance(locations, int):
                location_ids = [locations]
            elif isinstance(locations, list) and len(locations) == 1:
                locations = vals.get("location_ids")[0]
                if locations[0] == 4:
                    location_ids = [locations[1]]
                elif locations[0] == 6:
                    location_ids = locations[1]
            if location_ids:
                location = self.env["stock.location"].browse(location_ids)
                if location.company_id:
                    vals["company_id"] = location.company_id.id
        return super(Inventory, self).create(vals)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.product_ids.check_company(self.company_id):
            self.product_ids = [(5, 0, 0)]
        if not self.location_ids.check_company(self.company_id):
            if self.product_ids.mapped("location_id"):
                self.location_ids = [(6, self.product_ids.mapped("location_ids").ids)]
            else:
                self.locations_ids = [(5, 0, 0)]

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.line_ids,
            self.move_ids,
        ]
        return res


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _check_company_auto = True

    location_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    inventory_id = fields.Many2one(check_company=True)
    package_id = fields.Many2one(check_company=True)
