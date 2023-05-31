# Copyright 2023 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    parent_id = fields.Many2one(related="partner_id.parent_id")
    property_product_pricelist = fields.Many2one(
        "product.pricelist",
        "Pricelist",
        compute="_compute_property_fields",
        readonly=False,
        help="This pricelist will be used, instead of the default one, "
        "for sales to the current partner",
    )

    def get_property_fields(self, obj, properties):
        super(PartnerProperty, self).get_property_fields(obj, properties)
        for rec in self:
            # Pricelist may be stored as a property or dynamically computed
            rec.property_product_pricelist = obj.with_context(
                force_company=rec.company_id.id
            ).property_product_pricelist

    def write(self, vals):
        # Use the standard inverse method of property_product_pricelist
        if "property_product_pricelist" in vals:
            for rec in self:
                rec.partner_id.with_context(force_company=rec.company_id.id).write(
                    {"property_product_pricelist": vals["property_product_pricelist"]}
                )
        return super(PartnerProperty, self).write(vals)
