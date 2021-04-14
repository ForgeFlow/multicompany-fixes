# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategoryProperty(models.TransientModel):
    _inherit = "product.category.property"

    property_account_income_categ_id = fields.Many2one(
        comodel_name="account.account",
        string="Income Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="This account will be used when validating a customer invoice.",
    )
    property_account_expense_categ_id = fields.Many2one(
        comodel_name="account.account",
        string="Expense Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="The expense is accounted for when a vendor bill is validated, "
        "except in anglo-saxon accounting with perpetual inventory "
        "valuation in which case the expense (Cost of Goods Sold account) "
        "is recognized at the customer invoice validation.",
    )

    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.property_account_income_categ_id = rec.get_property_value(
                "property_account_income_categ_id", object, properties
            )
            rec.property_account_expense_categ_id = rec.get_property_value(
                "property_account_expense_categ_id", object, properties
            )

    def get_property_fields_list(self):
        res = super(ProductCategoryProperty, self).get_property_fields_list()
        res.append("property_account_income_categ_id")
        res.append("property_account_expense_categ_id")
        return res
