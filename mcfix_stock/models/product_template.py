from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    route_ids = fields.Many2many(check_company=True)
    route_from_categ_ids = fields.Many2many(check_company=True)

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
