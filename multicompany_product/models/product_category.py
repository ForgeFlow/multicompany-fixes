from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_ids = fields.One2many(
        comodel_name='product.category.property',
        inverse_name='categ_id',
        string='Properties'

    )


class ProductCategoryProperty(models.Model):
    _name = 'product.category.property'
    _inherit = 'multicompany.property.abstract'
    _description = "Properties of Product categories"

    categ_id = fields.Many2one(
        comodel_name='product.category'
    )

    _sql_constraints = [('company_category_unique',
                         'UNIQUE(company_id, categ_id)',
                         "The company must be unique"),
                        ]

    @api.model
    def create(self, vals):
        self.set_properties(self.env['product.category'].browse(vals.get('categ_id', False)), vals,
                            self.env['ir.property'].with_context(force_company=self.company_id.id))
        return super(ProductCategoryProperty, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            record.set_properties(record.categ_id, vals,
                                  self.env['ir.property'].with_context(force_company=record.company_id.id))
        return super(ProductCategoryProperty, self).write(vals)

    @api.model
    def set_properties(self, object, vals, properties=False):
        return
