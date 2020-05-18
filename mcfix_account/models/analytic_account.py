from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.move.line', [('analytic_account_id', '=', self.id)]),
            ('account.reconcile.model',
             [('analytic_account_id', '=', self.id)]),
            ('account.reconcile.model',
             [('second_analytic_account_id', '=', self.id)]),
        ]
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    product_id = fields.Many2one(check_company=True)
    move_id = fields.Many2one(check_company=True)
    general_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
