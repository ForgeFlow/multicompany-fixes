from odoo import models


class Route(models.Model):
    _inherit = 'stock.location.route'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order.line', [('route_id', '=', self.id)]),
        ]
        return res
