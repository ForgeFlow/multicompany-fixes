from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_id = fields.Many2one(readonly=True)


class ProductProperty(models.TransientModel):
    _inherit = 'product.template.property'

    project_id = fields.Many2one(
        comodel_name='project.project', string='Project',
        compute='_compute_property_fields',
        readonly=False,
        help='Create a task under this project on sale '
             'order validation. This setting must be set for each company.')

    type = fields.Selection(related='product_template_id.type')
    track_service = fields.Selection(
        related='product_template_id.track_service')

    @api.one
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(
            object, properties)
        self.project_id = self.get_property_value('project_id',
                                                  object, properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ProductProperty, self).set_properties(object, properties)
        self.set_property(object, 'project_id', self.project_id.id, properties)
