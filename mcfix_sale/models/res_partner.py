from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order', [('fiscal_position_id', '=', self.id)]),
        ]
        return res


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_ids, self.sale_order_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order.line', [('order_partner_id', '=', self.id)]),
        ]
        return res
