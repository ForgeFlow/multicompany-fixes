from odoo import models


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order', [('picking_ids', 'in', self.ids)]),
        ]
        return res
