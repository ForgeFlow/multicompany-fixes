from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(ProductTemplate, self)._onchange_company_id()
        if not self.route_ids.check_company(self.company_id) and self.ids:
            self.route_ids = self.env["stock.location.route"].search(
                [
                    ("product_ids", "in", [self.id]),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ]
            )

    route_ids = fields.Many2many(check_company=True)
