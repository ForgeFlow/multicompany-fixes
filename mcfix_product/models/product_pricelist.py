from odoo import api, models, _
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(Pricelist, self).name_get()
        res = self.add_company_suffix(names)
        return res


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Pricelist Item and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_tmpl_id')
    def _check_company_id_product_tmpl_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_tmpl_id.company_id and\
                    rec.company_id != rec.product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Pricelist Item and in '
                      'Product Template must be the same.'))
