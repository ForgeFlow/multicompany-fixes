from odoo import fields, models, api


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductCategory, self).get_properties()
        self.property_account_creditor_price_difference_categ = self.get_property(
            self.property, 'property_account_creditor_price_difference_categ', False)

    property_account_creditor_price_difference_categ = fields.Many2one(
        'account.account', compute='get_properties', default=get_properties,company_dependent=False)


class ProductCategoryProperty(models.Model):
    _inherit = 'product.category.property'

    property_account_creditor_price_difference_categ = fields.Many2one(
        'account.account', string="Price Difference Account",
        company_dependent=False,
        help="This account will be used to value price difference between purchase price and accounting cost.")
