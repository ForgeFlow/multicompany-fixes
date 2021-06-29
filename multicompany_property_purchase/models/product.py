# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductProperty(models.TransientModel):
    _inherit = "product.property"

    purchase_ok = fields.Boolean(related="product_template_id.purchase_ok")
    property_account_creditor_price_difference = fields.Many2one(
        "account.account",
        string="Price Difference Account",
        compute="_compute_property_fields",
        readonly=False,
        help="This account is used in automated inventory valuation to "
        "record the price difference between a purchase order and "
        "its related vendor bill when validating this vendor bill.",
    )

    def get_property_fields(self, obj, properties):
        super(ProductProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_account_creditor_price_difference = rec.get_property_value(
                "property_account_creditor_price_difference", obj, properties
            )

    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append("property_account_creditor_price_difference")
        return res
