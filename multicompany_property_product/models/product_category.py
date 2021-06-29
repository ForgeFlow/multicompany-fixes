# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_ids = fields.One2many(
        comodel_name="product.category.property",
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
            property_obj = self.env["product.category.property"]
            values = []
            for company in self.env.companies:
                val = property_obj.create(
                    {"categ_id": record.id, "company_id": company.id}
                )
                values.append(val.id)
            record.property_ids = values


class ProductCategoryProperty(models.TransientModel):
    _name = "product.category.property"
    _inherit = "model.property"
    _description = "Properties of Product categories"

    categ_id = fields.Many2one(comodel_name="product.category")

    def _compute_property_fields(self):
        self.ensure_one()
        obj = self.categ_id
        self.get_property_fields(
            obj, self.env["ir.property"].with_context(force_company=self.company_id.id),
        )

    def get_property_fields(self, obj, properties):
        return

    def write(self, vals):
        prop_obj = self.env["ir.property"].with_context(
            force_company=self.company_id.id
        )
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    self.set_property(rec.categ_id, field, vals[field], prop_obj)
        return super(ProductCategoryProperty, self).write(vals)
