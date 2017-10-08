# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProductTemplate, self).onchange_company_id()
        self.property_account_creditor_price_difference = False

    @api.multi
    @api.constrains('property_account_creditor_price_difference', 'company_id')
    def _check_company_property_account_creditor_price_difference(self):
        for template in self.sudo():
            if template.company_id and template.\
                    property_account_creditor_price_difference.company_id and \
                    template.company_id != template.\
                    property_account_creditor_price_difference.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Price Difference Account must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProductTemplate, self)._check_company_id()
        for rec in self:
            report = self.env['purchase.report'].search(
                [('product_tmpl_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Report '
                      '%s.' % report.name))
