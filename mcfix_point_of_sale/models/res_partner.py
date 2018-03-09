from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.config', [('default_fiscal_position_id', '=', self.id)]),
            ('pos.config', [('fiscal_position_ids', 'in', self.ids)]),
            ('pos.order', [('fiscal_position_id', '=', self.id)]),
        ]
        return res


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.order', [('partner_id', '=', self.id)]),
        ]
        return res
