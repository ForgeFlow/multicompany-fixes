from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ProductTemplate, self)._onchange_company_id()
        if not self.taxes_id.check_company(self.company_id):
            self.taxes_id = self.taxes_id.filtered(
                lambda t: t.company_id == self.company_id)
        if not self.supplier_taxes_id.check_company(self.company_id):
            self.supplier_taxes_id = self.supplier_taxes_id.filtered(
                lambda t: t.company_id == self.company_id)

    @api.multi
    @api.constrains('company_id', 'supplier_taxes_id')
    def _check_company_id_supplier_taxes_id(self):
        for rec in self.sudo():
            for line in rec.supplier_taxes_id:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'taxes_id')
    def _check_company_id_taxes_id(self):
        for rec in self.sudo():
            for line in rec.taxes_id:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.constrains('company_id', 'supplier_taxes_id')
    def _check_company_id_supplier_taxes_id(self):
        for rec in self.sudo():
            for line in rec.supplier_taxes_id:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Product and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'taxes_id')
    def _check_company_id_taxes_id(self):
        for rec in self.sudo():
            for line in rec.taxes_id:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Product and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])
