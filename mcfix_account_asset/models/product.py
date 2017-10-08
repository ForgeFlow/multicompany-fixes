# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProductTemplate, self).onchange_company_id()
        self.asset_category_id = False
        self.deferred_revenue_category_id = False

    @api.multi
    @api.constrains('asset_category_id', 'company_id')
    def _check_company_asset_category_id(self):
        for template in self.sudo():
            if template.company_id and template.asset_category_id.company_id \
                    and template.company_id != template.asset_category_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Asset Type must be the same.'))
        return True

    @api.multi
    @api.constrains('deferred_revenue_category_id', 'company_id')
    def _check_company_deferred_revenue_category_id(self):
        for template in self.sudo():
            if template.company_id and template.deferred_revenue_category_id.\
                    company_id and template.company_id != template.\
                    deferred_revenue_category_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Deferred Revenue Type must be the same.'))
        return True
