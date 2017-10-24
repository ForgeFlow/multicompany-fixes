# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProductTemplate, self).onchange_company_id()
        self.property_stock_account_input = False
        self.property_stock_account_output = False

    @api.multi
    @api.constrains('property_stock_account_input', 'company_id')
    def _check_company_property_stock_account_input(self):
        for template in self.sudo():
            if template.company_id and template.property_stock_account_input.\
                    company_id and template.company_id != template.\
                    property_stock_account_input.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Account Input must be the same.'))
        return True

    @api.multi
    @api.constrains('property_stock_account_output', 'company_id')
    def _check_company_property_stock_account_output(self):
        for template in self.sudo():
            if template.company_id and template.property_stock_account_output.\
                    company_id and template.company_id != template.\
                    property_stock_account_output.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Account Output must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProductTemplate, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            history = self.env['stock.history'].search(
                [('product_template_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if history:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to History '
                      '%s.' % history.name))
