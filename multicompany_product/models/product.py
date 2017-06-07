import odoo.addons.decimal_precision as dp

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(readonly=True)

    property_ids = fields.One2many(
        comodel_name='product.template.property',
        inverse_name='product_template_id',
        string='Properties'
    )


class ProductProperty(models.Model):
    _name = 'product.template.property'
    _inherit = 'multicompany.property.abstract'

    _description = "Properties of Product categories"

    product_template_id = fields.Many2one(
        comodel_name='product.template'
    )

    _sql_constraints = [('company_product_template_unique',
                         'UNIQUE(company_id, product_template_id)',
                         "The company must be unique"),
                        ]

    @api.model
    def create(self, vals):
        self.set_properties(self.env['product.template'].browse(vals.get('product_template_id', False)), vals,
                            self.env['ir.property'].with_context(force_company=self.company_id.id))
        return super(ProductProperty, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            record.set_properties(record.product_template_id, vals,
                                  self.env['ir.property'].with_context(force_company=record.company_id.id))
        return super(ProductProperty, self).write(vals)

    standard_price = fields.Float(
        'Cost',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('standard_price', False):
            self.set_property(object, 'standard_price', vals.get('standard_price', False), properties)
