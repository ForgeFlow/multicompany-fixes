from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_purchase_currency_id = fields.Many2one(readonly=True)


class ResPartnerProperties(models.Model):
    _inherit = 'res.partner.property'

    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency",
        help="This currency will be used, instead of the default one, for purchases from the current partner")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_purchase_currency_id', False):
            self.set_property(object, 'property_purchase_currency_id', vals.get('property_purchase_currency_id', False),
                              properties)
        return super(ResPartnerProperties, self).set_properties(object, vals, properties)
