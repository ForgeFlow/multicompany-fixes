# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    property_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Customer Analytic Account",
        compute="_compute_property_fields",
        readonly=False,
        help="Default Analytic Account used for Purchase Orders and Vendor Bills",
    )

    property_supplier_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Vendor Analytic Account",
        compute="_compute_property_fields",
        readonly=False,
        help="Default Analytic Account used for Purchase Orders and Vendor Bills",
    )

    def get_property_fields(self, obj, properties):
        res = super(ResPartnerProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_analytic_account_id = rec.get_property_value(
                "property_analytic_account_id", obj, properties
            )
            rec.property_supplier_analytic_account_id = rec.get_property_value(
                "property_supplier_analytic_account_id", obj, properties
            )
        return res

    def get_property_fields_list(self):
        res = super(ResPartnerProperty, self).get_property_fields_list()
        res.append("property_analytic_account_id")
        res.append("property_supplier_analytic_account_id")
        return res
