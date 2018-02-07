from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(ProductProduct, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def write(self, values):
        if values.get('company_id'):
            res = super(ProductProduct, self.with_context(
                bypass_company_validation=True)).write(values)
            if self.product_tmpl_id.company_id and \
                    self.product_tmpl_id.company_id.id != values['company_id']:
                self.product_tmpl_id.write(
                    {'company_id': values['company_id']})
        else:
            res = super(ProductProduct, self).write(values)
        return res

    @api.multi
    def _set_standard_price(self, value):
        """ Store the standard price change in order to be able to retrieve
        the cost of a product for a given date """
        for product in self:
            if product.company_id:
                product = product.with_context(
                    force_company=product.company_id.id)
            super(ProductProduct, product)._set_standard_price(value)

    @api.multi
    @api.constrains('company_id', 'pricelist_id')
    def _check_company_id_pricelist_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.pricelist_id.company_id and\
                    rec.company_id != rec.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Product and in '
                      'Product Pricelist must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_tmpl_id')
    def _check_company_id_product_tmpl_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_tmpl_id.company_id and\
                    rec.company_id != rec.product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Product and in '
                      'Product Template must be the same.'))
