# Copyright 2021 Creu Blanca
# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    property_ids = fields.One2many(
        comodel_name="account.tax.group.property",
        compute="_compute_properties",
        inverse="_inverse_properties",
        string="Properties",
    )

    def _inverse_properties(self):
        """ Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable. """
        return

    def _compute_properties(self):
        for record in self:
            property_obj = self.env["account.tax.group.property"]
            values = []
            for company in self.env.companies:
                val = property_obj.create(
                    {"tax_group_id": record.id, "company_id": company.id}
                )
                values.append(val.id)
            record.property_ids = values


class AccountTaxGroupProperty(models.TransientModel):
    _name = "account.tax.group.property"
    _inherit = "model.property"
    _description = "Properties of Tax groups"

    tax_group_id = fields.Many2one(comodel_name="account.tax.group")
    property_tax_payable_account_id = fields.Many2one(
        "account.account",
        compute="_compute_property_fields",
        readonly=False,
        string="Tax current account (payable)",
    )
    property_tax_receivable_account_id = fields.Many2one(
        "account.account",
        compute="_compute_property_fields",
        readonly=False,
        string="Tax current account (receivable)",
    )
    property_advance_tax_payment_account_id = fields.Many2one(
        "account.account",
        compute="_compute_property_fields",
        readonly=False,
        string="Advance Tax payment account",
    )

    def _compute_property_fields(self):
        self.ensure_one()
        object = self.tax_group_id
        self.get_property_fields(
            object,
            self.env["ir.property"].with_context(force_company=self.company_id.id),
        )

    def get_property_fields(self, object, properties):
        for rec in self:
            rec.property_tax_payable_account_id = rec.get_property_value(
                "property_tax_payable_account_id", object, properties
            )
            rec.property_tax_receivable_account_id = rec.get_property_value(
                "property_tax_receivable_account_id", object, properties
            )
            rec.property_advance_tax_payment_account_id = rec.get_property_value(
                "property_advance_tax_payment_account_id", object, properties
            )

    def get_property_fields_list(self):
        res = super(AccountTaxGroupProperty, self).get_property_fields_list()
        res.append("property_tax_payable_account_id")
        res.append("property_tax_receivable_account_id")
        res.append("property_advance_tax_payment_account_id")
        return res

    def write(self, vals):
        prop_obj = self.env["ir.property"].with_context(
            force_company=self.company_id.id
        )
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    self.set_property(rec.tax_group_id, field, vals[field], prop_obj)
        return super(AccountTaxGroupProperty, self).write(vals)
