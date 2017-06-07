from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_stock_customer = fields.Many2one(readonly=True)
    property_stock_supplier = fields.Many2one(readonly=True)


class ResPartnerProperties(models.Model):
    _inherit = 'res.partner.property'

    property_stock_customer = fields.Many2one(
        'stock.location', string="Customer Location",
        help="This stock location will be used, instead of the default one, as the destination location for goods you send to this partner")
    property_stock_supplier = fields.Many2one(
        'stock.location', string="Vendor Location",
        help="This stock location will be used, instead of the default one, as the source location for goods you receive from the current partner")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_stock_customer', False):
            self.set_property(object, 'property_stock_customer', vals.get('property_stock_customer', False),
                              properties)
        if vals.get('property_stock_supplier', False):
            self.set_property(object, 'property_stock_supplier', vals.get('property_stock_supplier', False),
                              properties)
        return super(ResPartnerProperties, self).set_properties(object, vals, properties)