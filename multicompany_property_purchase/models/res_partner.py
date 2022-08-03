# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperties(models.TransientModel):
    _inherit = "res.partner.property"

    property_purchase_currency_id = fields.Many2one(
        "res.currency",
        string="Supplier Currency",
        compute="_compute_property_fields",
        readonly=False,
        help="This currency will be used, instead of the "
        "default one, for purchases from the current partner",
    )

    def get_property_fields(self, obj, properties):
        res = super(PartnerProperties, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_purchase_currency_id = rec.get_property_value(
                "property_purchase_currency_id", obj, properties
            )
        return res

    def get_property_fields_list(self):
        res = super(PartnerProperties, self).get_property_fields_list()
        res.append("property_purchase_currency_id")
        return res
