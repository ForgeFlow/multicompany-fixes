from odoo import models, api, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ResPartner, self).get_properties()
        ir_property_obj = self.env['ir.property']
        self.property_stock_customer = self.get_property(
            self.property, 'property_stock_customer', ir_property_obj.get('property_stock_customer', 'res.partner'))
        self.property_stock_supplier = self.get_property(
            self.property, 'property_stock_supplier', ir_property_obj.get('property_stock_supplier', 'res.partner'))

    property_stock_customer = fields.Many2one(
        'stock.location', company_dependent=False,
        default=get_properties, compute='get_properties',
    )
    property_stock_supplier = fields.Many2one(
        'stock.location', company_dependent=False,
        default=get_properties, compute='get_properties', )


class ResPartnerProperty(models.Model):
    _inherit = 'res.partner.property'

    property_stock_customer = fields.Many2one(
        'stock.location', string="Customer Location",
        help="This stock location will be used, instead of the default one, as the destination location for goods you send to this partner")
    property_stock_supplier = fields.Many2one(
        'stock.location', string="Vendor Location",
        help="This stock location will be used, instead of the default one, as the source location for goods you receive from the current partner")
