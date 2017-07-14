# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def get_property_product_pricelist(self):
        return self.env['ir.property'].with_context(force_company=self.id).get(
            'property_product_pricelist', 'res.partner')

    property_product_pricelist = fields.Many2One(
        comodel_name='product.pricelist',
        string='Pricelist',
        default=get_property_product_pricelist,
        store=False
    )
