from odoo import models, fields, api
from odoo.exceptions import MissingError


class MulticomanyPropertyAbstract(models.AbstractModel):
    _name = 'multicompany.property.abstract'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        readonly=True
    )

    @api.one
    def _compute_property_fields(self):
        raise MissingError('It must be redefined')

    # This is the function we will extend in order to generate the information
    @api.one
    def get_property_fields(self, object, properties):
        raise MissingError('It must be redefined')

    # This is the function we will extend in order to generate the information
    @api.model
    def set_properties(self, object, properties=False):
        raise MissingError('It must be redefined')

    def set_property(self, object, fieldname, value, properties):
        properties.set_multi(fieldname, object._name, {object.id: value})

    def get_property_value(self, field, object, prop_obj):
        value = prop_obj.get(field, object._name, (object._name + ',%s') % object.id)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        value = prop_obj.get(field, object._name)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        return False
