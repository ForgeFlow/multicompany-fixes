from odoo import api, models, _
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.multi
    @api.constrains('company_id', 'product_tmpl_id')
    def _check_company_id_product_tmpl_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_tmpl_id.company_id and\
                    rec.company_id != rec.product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Product Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'name')
    def _check_company_id_name(self):
        for rec in self.sudo():
            if rec.company_id and rec.name.company_id and\
                    rec.company_id != rec.name.company_id:
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Supplierinfo and in '
                      'Product Product must be the same.'))
