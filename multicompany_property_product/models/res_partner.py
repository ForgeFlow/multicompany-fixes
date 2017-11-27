from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_product_pricelist = fields.Many2one(readonly=True)


class ResPartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_product_pricelist = fields.Many2one(
        'product.pricelist',
        string="Sale Pricelist",
        compute='_compute_property_fields',
        readonly=False,
        store=False,
        help="This pricelist will be used, instead of the default one, "
             "for sales to the current partner.")

    @api.one
    def get_property_fields(self, object, properties):
        super(ResPartnerProperty, self).get_property_fields(object, properties)
        self.property_product_pricelist = self.get_property_value(
            'property_product_pricelist', object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ResPartnerProperty, self).get_property_fields_list()
        res.append('property_product_pricelist')
        return res

    @api.model
    def set_properties(self, object, properties=False):
        super(ResPartnerProperty, self).set_properties(object, properties)
        self.set_property(object, 'property_product_pricelist',
                          self.property_product_pricelist.id, properties)
