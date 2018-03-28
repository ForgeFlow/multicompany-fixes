from odoo import models


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('procurement.rule', [('partner_address_id', '=', self.id)]),
            ('stock.inventory', [('partner_id', '=', self.id)]),
            ('stock.inventory.line', [('partner_id', '=', self.id)]),
            ('stock.location', [('partner_id', '=', self.id)]),
            ('stock.move', [('restrict_partner_id', '=', self.id)]),
            ('stock.move', [('partner_id', '=', self.id)]),
            ('stock.move.line', [('owner_id', '=', self.id)]),
            ('stock.picking', [('partner_id', '=', self.id)]),
            ('stock.picking', [('owner_id', '=', self.id)]),
            ('stock.quant', [('owner_id', '=', self.id)]),
            ('stock.scrap', [('owner_id', '=', self.id)]),
            ('stock.warehouse', [('partner_id', '=', self.id)]),
        ]
        return res
