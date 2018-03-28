from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('report.all.channels.sales',
             [('analytic_account_id', '=', self.id)]),
            ('sale.order', [('analytic_account_id', '=', self.id)]),
            ('sale.report', [('analytic_account_id', '=', self.id)]),
        ]
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('company_id', 'so_line')
    def _check_company_id_so_line(self):
        for rec in self.sudo():
            if not rec.so_line.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Sale Order Line must be the same.'))
