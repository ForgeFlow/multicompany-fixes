# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_creditor_price_difference = fields.Many2one(readonly=True)


class ProductProperty(models.TransientModel):
    _inherit = 'product.property'

    purchase_ok = fields.Boolean(related='product_template_id.purchase_ok')
    property_account_creditor_price_difference = fields.Many2one(
        'account.account', string="Price Difference Account",
        compute='_compute_property_fields',
        readonly=False,
        help="This account will be used to value price difference "
             "between purchase price and cost price.")

    @api.one
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(object, properties)
        self.property_account_creditor_price_difference = \
            self.get_property_value(
                'property_account_creditor_price_difference',
                object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append('property_account_creditor_price_difference')
        return res

    @api.model
    def set_properties(self, object, properties=False):
        super(ProductProperty, self).set_properties(object, properties)
        self.set_property(
            object, 'property_account_creditor_price_difference',
            self.property_account_creditor_price_difference.id, properties)
