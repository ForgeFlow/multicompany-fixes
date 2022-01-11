# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCategoryProperty(models.TransientModel):
    _inherit = "product.category.property"

    income_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Income Analytic Account",
        compute="_compute_property_fields",
        readonly=False,
    )
    expense_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Expense Analytic Account",
        compute="_compute_property_fields",
        readonly=False,
    )

    def get_property_fields(self, obj, properties):
        super(ProductCategoryProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.income_analytic_account_id = rec.get_property_value(
                "income_analytic_account_id", obj, properties
            )
            rec.expense_analytic_account_id = rec.get_property_value(
                "expense_analytic_account_id", obj, properties
            )

    def get_property_fields_list(self):
        res = super(ProductCategoryProperty, self).get_property_fields_list()
        res.append("income_analytic_account_id")
        res.append("expense_analytic_account_id")
        return res
