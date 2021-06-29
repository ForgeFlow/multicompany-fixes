from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    _check_company_auto = True

    journal_id = fields.Many2one(check_company=True)
    line_ids = fields.One2many(check_company=True)
    move_line_ids = fields.One2many(check_company=True)

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    _check_company_auto = True

    account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
    statement_id = fields.Many2one(check_company=True)
    bank_account_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    journal_entry_ids = fields.One2many(check_company=True)

    def _prepare_reconciliation_move(self, move_ref):
        result = super()._prepare_reconciliation_move(move_ref)
        result["company_id"] = self.statement_id.company_id.id
        return result

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
