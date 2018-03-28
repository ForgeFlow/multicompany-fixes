from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.invoice.line', [('account_analytic_id', '=', self.id)]),
            ('account.invoice.tax', [('account_analytic_id', '=', self.id)]),
            ('account.move.line', [('analytic_account_id', '=', self.id)]),
            ('account.reconcile.model',
             [('analytic_account_id', '=', self.id)]),
            ('account.reconcile.model',
             [('second_analytic_account_id', '=', self.id)]),
        ]
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if not rec.move_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Account Move Line must be the same.'))
