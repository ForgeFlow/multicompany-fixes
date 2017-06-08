from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    asset_category_id = fields.Many2one(readonly=True)
    deferred_revenue_category_id = fields.Many2one(readonly=True)


class ProductProperty(models.Model):
    _inherit = 'product.template.property'

    asset_category_id = fields.Many2one('account.asset.category', string='Asset Type', ondelete="restrict")
    deferred_revenue_category_id = fields.Many2one('account.asset.category', string='Deferred Revenue Type',
                                                   ondelete="restrict")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('asset_category_id', False):
            self.set_property(object, 'asset_category_id',
                              vals.get('asset_category_id', False), properties)
        if vals.get('deferred_revenue_category_id', False):
            self.set_property(object, 'deferred_revenue_category_id',
                              vals.get('deferred_revenue_category_id', False), properties)
        return super(ProductProperty, self).set_properties(object, vals, properties)