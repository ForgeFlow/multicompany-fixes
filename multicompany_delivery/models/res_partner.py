from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_delivery_carrier_id = fields.Many2one(readonly=True)


class ResPartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_delivery_carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Delivery Method",
        compute='get_properties',
        readonly=False,
        store=False,
        help="This delivery method will be used when invoicing from picking.")

    @api.one
    def get_property_fields(self, object, properties):
        super(ResPartnerProperty, self).get_property_fields(object, properties)
        self.property_delivery_carrier_id = self.get_property_value('property_delivery_carrier_id', object, properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ResPartnerProperty, self).set_properties(object, properties)
        self.set_property(object, 'property_delivery_carrier_id', self.property_delivery_carrier_id.id, properties)
