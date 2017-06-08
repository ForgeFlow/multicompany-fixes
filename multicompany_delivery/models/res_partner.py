from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_delivery_carrier_id = fields.Many2one(readonly=True)


class ResPartnerProperties(models.Model):
    _inherit = 'res.partner.property'

    property_delivery_carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                                   help="This delivery method will be used when invoicing from picking.")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_delivery_carrier_id', False):
            self.set_property(object, 'property_delivery_carrier_id', vals.get('property_delivery_carrier_id', False),
                              properties)
        return super(ResPartnerProperties, self).set_properties(object, vals, properties)
