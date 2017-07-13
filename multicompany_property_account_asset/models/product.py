from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    asset_category_id = fields.Many2one(readonly=True)
    deferred_revenue_category_id = fields.Many2one(readonly=True)


class ProductProperty(models.TransientModel):
    _inherit = 'multicompany.property.product'

    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Asset Type',
        compute='_compute_property_fields',
        readonly=False,
        ondelete="restrict")
    deferred_revenue_category_id = fields.Many2one(
        'account.asset.category',
        string='Deferred Revenue Type',
        compute='_compute_property_fields',
        readonly=False,
        ondelete="restrict")

    @api.one
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(object, properties)
        self.asset_category_id = self.get_property_value('asset_category_id',
                                                         object, properties)
        self.deferred_revenue_category_id =\
            self.get_property_value('deferred_revenue_category_id', object,
                                    properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ProductProperty, self).set_properties(object, properties)
        self.set_property(object, 'asset_category_id',
                          self.asset_category_id.id, properties)
        self.set_property(object, 'deferred_revenue_category_id',
                          self.deferred_revenue_category_id.id, properties)
