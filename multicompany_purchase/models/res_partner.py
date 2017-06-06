from odoo import fields, models, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ResPartner,self).get_properties()

        self.property_purchase_currency_id = self.get_property(
            self.property, 'property_purchase_currency_id', self.current_company_id.currency_id)

    property_purchase_currency_id = fields.Many2one(
        'res.currency',
        company_dependent=False, default=get_properties, compute='get_properties')


class ResPartnerProperties(models.Model):
    _inherit = 'res.partner.property'

    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency", company_dependent=False,
        help="This currency will be used, instead of the default one, for purchases from the current partner")
