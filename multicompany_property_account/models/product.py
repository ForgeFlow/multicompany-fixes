# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductProperty(models.TransientModel):
    _inherit = "product.property"

    property_account_income_id = fields.Many2one(
        comodel_name="account.account",
        string="Income Account",
        domain=[("deprecated", "=", False)],
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="Keep this field empty to use the default value from the "
        "product category.",
    )
    property_account_expense_id = fields.Many2one(
        comodel_name="account.account",
        string="Expense Account",
        domain=[("deprecated", "=", False)],
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="Keep this field empty to use the default value from the "
        "product category. If anglo-saxon accounting with automated "
        "valuation method is configured, the expense account on the "
        "product category will be used.",
    )

    def get_property_fields(self, obj, properties):
        res = super(ProductProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_account_income_id = rec.get_property_value(
                "property_account_income_id", obj, properties
            )
            rec.property_account_expense_id = rec.get_property_value(
                "property_account_expense_id", obj, properties
            )
        return res

    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append("property_account_income_id")
        res.append("property_account_expense_id")
        return res
