# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_ids = fields.One2many(
        comodel_name="product.property",
        compute="_compute_properties",
        inverse="_inverse_properties",
        string="Properties",
    )

    def _inverse_properties(self):
        """Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable."""
        return

    def _compute_properties(self):
        for record in self:
            property_obj = self.env["product.property"]
            for company in self.env.companies:
                val = property_obj.create(
                    {"company_id": company.id, "product_template_id": record.id}
                )
                record.property_ids += val


class ProductProduct(models.Model):
    _inherit = "product.product"

    property_ids = fields.One2many(
        comodel_name="product.property",
        compute="_compute_properties",
        inverse="_inverse_properties",
        string="Properties",
    )

    def _inverse_properties(self):
        """Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable."""
        return

    def _compute_properties(self):
        for record in self:
            property_obj = self.env["product.property"]
            for company in self.env.companies:
                val = property_obj.create(
                    {
                        "company_id": company.id,
                        "product_id": record.id,
                        "product_template_id": record.product_tmpl_id.id,
                    }
                )
                record.property_ids += val


class ProductProperty(models.TransientModel):
    _name = "product.property"
    _inherit = "model.property"

    _description = "Properties of Products"

    product_template_id = fields.Many2one(
        comodel_name="product.template", string="Product Template"
    )
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    standard_price = fields.Float(
        "Cost",
        digits="Product Price",
        groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product
        (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known
        (e.g. inventory adjustment). Used to compute margins on sale orders.""",
        compute="_compute_property_fields",
        readonly=False,
    )

    def _compute_property_fields(self):
        for rec in self:
            obj = rec.product_id or rec.product_template_id
            rec.get_property_fields(
                obj,
                rec.env["ir.property"].with_context(force_company=rec.company_id.id),
            )

    def get_property_fields(self, obj, properties):
        for rec in self:
            if obj._name == "product.template":
                if len(obj.product_variant_ids) == 1:
                    variant = obj.product_variant_ids[0]
                    rec.standard_price = rec.get_property_value(
                        "standard_price", variant, properties
                    )
                else:
                    rec.standard_price = 0.0
            elif obj._name == "product.product":
                rec.standard_price = rec.get_property_value(
                    "standard_price", obj, properties
                )

    def write(self, vals):
        """Standard price do not follow the usual workflow
        as it has special considerations"""
        prop_obj = self.env["ir.property"].with_context(
            force_company=self.company_id.id
        )
        if "standard_price" in vals:
            for rec in self:
                obj = rec.product_id or rec.product_template_id
                obj = obj.with_context(force_company=rec.company_id.id)
                if obj._name == "product.template":
                    for pv in obj.product_variant_ids:
                        self.set_property(
                            pv, "standard_price", vals["standard_price"], prop_obj
                        )
                elif obj._name == "product.product":
                    self.set_property(
                        obj, "standard_price", vals["standard_price"], prop_obj
                    )
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    obj = rec.product_id or rec.product_template_id
                    self.set_property(obj, field, vals[field], prop_obj)
        return super(ProductProperty, self).write(vals)
