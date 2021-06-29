# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    property_stock_customer = fields.Many2one(
        "stock.location",
        string="Customer Location",
        compute="_compute_property_fields",
        readonly=False,
        domain="['|', ('company_id', '=', False),"
        "('company_id', '=', allowed_company_ids[0])]",
        help="The stock location used as destination when sending "
        "goods to this contact.",
    )
    property_stock_supplier = fields.Many2one(
        "stock.location",
        string="Vendor Location",
        compute="_compute_property_fields",
        readonly=False,
        domain="['|', ('company_id', '=', False),"
        "('company_id', '=', allowed_company_ids[0])]",
        help="The stock location used as source when receiving "
        "goods from this contact.",
    )

    def get_property_fields(self, obj, properties):
        super(PartnerProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_stock_customer = rec.get_property_value(
                "property_stock_customer", obj, properties
            )
            rec.property_stock_supplier = rec.get_property_value(
                "property_stock_supplier", obj, properties
            )

    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append("property_stock_customer")
        res.append("property_stock_supplier")
        return res
