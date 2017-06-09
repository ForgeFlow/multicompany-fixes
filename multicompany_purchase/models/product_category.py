from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_creditor_price_difference_categ = fields.Many2one(readonly=True)


class ProductCategoryProperty(models.TransientModel):
    _inherit = 'product.category.property'

    property_account_creditor_price_difference_categ = fields.Many2one(
        'account.account', string="Price Difference Account",
        compute='_compute_property_fields',
        readonly=False,
        help="This account will be used to value price "
             "difference between purchase price and accounting cost.")

    @api.one
    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(
            object, properties)
        self.property_account_creditor_price_difference_categ = \
            self.get_property_value(
                'property_account_creditor_price_difference_categ',
                object, properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ProductCategoryProperty, self).set_properties(object, properties)
        self.set_property(
            object, 'property_account_creditor_price_difference_categ',
            self.property_account_creditor_price_difference_categ.id,
            properties)
