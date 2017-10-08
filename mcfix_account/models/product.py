# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProductTemplate, self).onchange_company_id()
        self.taxes_id = False
        self.supplier_taxes_id = False
        self.property_account_income_id = False
        self.property_account_expense_id = False

    @api.multi
    @api.constrains('taxes_id', 'company_id')
    def _check_company_taxes_id(self):
        for template in self.sudo():
            for account_tax in template.taxes_id:
                if template.company_id and account_tax.company_id and \
                        template.company_id != account_tax.company_id:
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Customer Taxes must be the same.'))
        return True

    @api.multi
    @api.constrains('supplier_taxes_id', 'company_id')
    def _check_company_supplier_taxes_id(self):
        for template in self.sudo():
            for account_tax in template.supplier_taxes_id:
                if template.company_id and account_tax.company_id and \
                        template.company_id != account_tax.company_id:
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Vendor Taxes must be the same.'))
        return True

    @api.multi
    @api.constrains('property_account_income_id', 'company_id')
    def _check_company_property_account_income_id(self):
        for template in self.sudo():
            if template.company_id and template.property_account_income_id.\
                    company_id and template.company_id != template.\
                    property_account_income_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Income Account must be the same.'))
        return True

    @api.multi
    @api.constrains('property_account_expense_id', 'company_id')
    def _check_company_property_account_expense_id(self):
        for template in self.sudo():
            if template.company_id and template.property_account_expense_id.\
                    company_id and template.company_id != template.\
                    property_account_expense_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Expense Account must be the same.'))
        return True
