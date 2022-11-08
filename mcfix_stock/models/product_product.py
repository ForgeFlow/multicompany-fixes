from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if not line.check_company(rec):
                    raise ValidationError(
                        _('The Company in the Product Product and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'route_from_categ_ids')
    def _check_company_id_route_from_categ_ids(self):
        for rec in self.sudo():
            for line in rec.route_from_categ_ids:
                if not line.check_company(rec):
                    raise ValidationError(
                        _('The Company in the Product Product and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])
