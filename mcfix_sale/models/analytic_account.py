from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("report.all.channels.sales", [("analytic_account_id", "=", self.id)]),
            ("sale.order", [("analytic_account_id", "=", self.id)]),
            ("sale.report", [("analytic_account_id", "=", self.id)]),
        ]
        return res


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    so_line = fields.Many2one(check_company=True)
