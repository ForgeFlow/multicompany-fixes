from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_creditor_price_difference = fields.Many2one(readonly=True)


class ProductProperty(models.Model):
    _inherit = 'product.template.property'

    purchase_ok = fields.Boolean(related='product_template_id.purchase_ok')
    property_account_creditor_price_difference = fields.Many2one(
        'account.account', string="Price Difference Account", company_dependent=False,
        help="This account will be used to value price difference between purchase price and cost price.")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_account_creditor_price_difference', False):
            self.set_property(object, 'property_account_creditor_price_difference',
                              vals.get('property_account_creditor_price_difference', False), properties)
        return super(ProductProperty, self).set_properties(object, vals, properties)
