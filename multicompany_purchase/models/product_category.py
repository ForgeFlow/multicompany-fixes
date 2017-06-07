from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_creditor_price_difference_categ = fields.Many2one(readonly=True)


class ProductCategoryProperty(models.Model):
    _inherit = 'product.category.property'

    property_account_creditor_price_difference_categ = fields.Many2one(
        'account.account', string="Price Difference Account",
        company_dependent=False,
        help="This account will be used to value price difference between purchase price and accounting cost.")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_account_creditor_price_difference_categ', False):
            self.set_property(object, 'property_account_creditor_price_difference_categ',
                              vals.get('property_account_creditor_price_difference_categ', False), properties)
        return super(ProductCategoryProperty, self).set_properties(object, vals, properties)
