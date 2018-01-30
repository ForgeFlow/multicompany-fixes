# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_id = fields.Many2one(readonly=True)


class ProductProperty(models.TransientModel):
    _inherit = 'product.property'

    project_id = fields.Many2one(
        comodel_name='project.project', string='Project',
        compute='_compute_property_fields',
        readonly=False,
        help='Create a task under this project on sale '
             'order validation. This setting must be set for each company.')

    type = fields.Selection(related='product_template_id.type')
    service_type = fields.Selection(
        related='product_template_id.service_type')

    @api.multi
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(
            object, properties)
        for rec in self:
            rec.project_id = rec.get_property_value('project_id',
                                                    object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append('project_id')
        return res
