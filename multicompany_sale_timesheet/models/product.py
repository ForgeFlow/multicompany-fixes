from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_id = fields.Many2one(readonly=True)


class ProductProperty(models.Model):
    _inherit = 'product.template.property'

    project_id = fields.Many2one(
        'project.project', 'Project',
        help='Create a task under this project on sale order validation. This setting must be set for each company.')

    type = fields.Selection(related='product_template_id.type')
    track_service = fields.Selection(related='product_template_id.track_service')

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('project_id', False):
            self.set_property(object, 'project_id',
                              vals.get('project_id', False), properties)
        return super(ProductProperty, self).set_properties(object, vals, properties)
