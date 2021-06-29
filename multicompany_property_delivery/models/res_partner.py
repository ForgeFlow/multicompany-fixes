# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    property_delivery_carrier_id = fields.Many2one(
        "delivery.carrier",
        compute="_compute_property_fields",
        readonly=False,
        string="Delivery Method",
        help="Default delivery method used in sales orders.",
    )

    def get_property_fields(self, obj, properties):
        super(PartnerProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_delivery_carrier_id = rec.get_property_value(
                "property_delivery_carrier_id", obj, properties
            )

    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append("property_delivery_carrier_id")
        return res
