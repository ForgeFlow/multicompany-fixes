# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategoryProperty(models.TransientModel):
    _inherit = "product.category.property"

    property_account_creditor_price_difference_categ = fields.Many2one(
        "account.account",
        string="Price Difference Account",
        compute="_compute_property_fields",
        readonly=False,
        help="This account will be used to value price "
        "difference between purchase price and accounting cost.",
    )

    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(object, properties)
        for rec in self:
            val = rec.get_property_value(
                "property_account_creditor_price_difference_categ", object, properties
            )
            rec.property_account_creditor_price_difference_categ = val

    def get_property_fields_list(self):
        res = super(ProductCategoryProperty, self).get_property_fields_list()
        res.append("property_account_creditor_price_difference_categ")
        return res
