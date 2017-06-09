from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_purchase_currency_id = fields.Many2one(readonly=True)


class ResPartnerProperties(models.TransientModel):
    _inherit = 'res.partner.property'

    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency",
        compute='_compute_property_fields',
        readonly=False,
        help="This currency will be used, instead of the "
             "default one, for purchases from the current partner")

    @api.one
    def get_property_fields(self, object, properties):
        super(ResPartnerProperties, self).get_property_fields()
        self.property_purchase_currency_id = \
            self.get_property_value('property_purchase_currency_id',
                                    object, properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ResPartnerProperties, self).set_properties()
        self.set_property(object,
                          'property_purchase_currency_id',
                          self.property_purchase_currency_id.id, properties)
