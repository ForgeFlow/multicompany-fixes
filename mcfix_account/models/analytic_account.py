from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    _check_company_auto = True

    reconcile_model_ids = fields.One2many(
        "account.reconcile.model",
        inverse_name="analytic_account_id",
        check_company=True,
    )
    second_reconcile_model_ids = fields.One2many(
        "account.reconcile.model",
        inverse_name="second_analytic_account_id",
        check_company=True,
    )

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    product_id = fields.Many2one(check_company=True)
    move_id = fields.Many2one(check_company=True)
    general_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]"
    )
