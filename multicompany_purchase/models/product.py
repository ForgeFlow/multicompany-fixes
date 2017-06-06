from odoo import models, fields, api


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductTemplate, self).get_properties()

        self.property_account_creditor_price_difference = self.get_property(
            self.property, 'property_account_creditor_price_difference', False)

    property_account_creditor_price_difference = fields.Many2one(
        'account.account', company_dependent=False,
        default=get_properties, compute='get_properties')


class ProductProperty(models.Model):
    _inherit = 'product.template.property'
    purchase_ok = fields.Boolean(related='product_id.purchase_ok')
    property_account_creditor_price_difference = fields.Many2one(
        'account.account', string="Price Difference Account", company_dependent=False,
        help="This account will be used to value price difference between purchase price and cost price.")
