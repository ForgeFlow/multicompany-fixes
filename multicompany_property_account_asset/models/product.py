# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class ProductProperty(models.TransientModel):
    _inherit = 'product.property'

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

    @api.multi
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.asset_category_id = rec.get_property_value('asset_category_id',
                                                           object, properties)
            rec.deferred_revenue_category_id = \
                rec.get_property_value('deferred_revenue_category_id', object,
                                       properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append('asset_category_id')
        res.append('deferred_revenue_category_id')
        return res
