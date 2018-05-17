from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    @api.constrains('company_id')
    def _check_company_id_route_from_categ_ids(self):
        for rec in self.sudo():
            for line in rec.route_from_categ_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.route_ids, self.route_from_categ_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.location.route', [('product_ids', 'in', self.ids)]),
        ]
        return res
