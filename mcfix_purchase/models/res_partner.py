from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order', [('fiscal_position_id', '=', self.id)]),
        ]
        return res


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order', [('partner_id', '=', self.id)]),
            ('purchase.order', [('dest_address_id', '=', self.id)]),
            ('purchase.order.line', [('partner_id', '=', self.id)]),
        ]
        return res
