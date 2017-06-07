from odoo import models, fields, api
from odoo.exceptions import MissingError


class MulticomanyPropertyAbstract(models.AbstractModel):
    _name = 'multicompany.property.abstract'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )

    @api.model
    def set_properties(self, object, vals, properties=False):
        raise MissingError('It must be redefined')

    @api.model
    def set_property(self, object, fieldname, value, properties=False):
        if not properties:
            properties = self.env['ir.property'].with_context(force_company=self.company_id.id)
        properties.set_multi(fieldname, object._name, {object.id: value})
