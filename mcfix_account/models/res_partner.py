from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"
    _check_company_auto = True

    move_ids = fields.One2many(
        "account.move", inverse_name="fiscal_position_id", check_company=True
    )

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.company_id and self.tax_ids:
            for tax in self.tax_ids:
                if not tax.tax_src_id.check_company(self.company_id):
                    tax.tax_src_id = False
                if not tax.tax_dest_id.check_company(self.company_id):
                    tax.tax_dest_id = False
        if self.company_id and self.account_ids:
            for account in self.account_ids:
                if not account.account_src_id.check_company(self.company_id):
                    account.account_src_id = False
                if not account.account_dest_id.check_company(self.company_id):
                    account.account_dest_id = False

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company", string="Company", related="position_id.company_id", store=True
    )
    tax_src_id = fields.Many2one(check_company=True)
    tax_dest_id = fields.Many2one(check_company=True)


class AccountFiscalPositionAccount(models.Model):
    _inherit = "account.fiscal.position.account"
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company", string="Company", related="position_id.company_id", store=True
    )
    account_src_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
    account_dest_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )


class Partner(models.Model):
    _inherit = "res.partner"

    property_account_position_id = fields.Many2one(
        domain="[('company_id', '=', current_company_id)]"
    )
    property_payment_term_id = fields.Many2one(
        domain="[('company_id', 'in', [current_company_id, False])]"
    )
    property_supplier_payment_term_id = fields.Many2one(
        domain="[('company_id', 'in', [current_company_id, False])]"
    )
    invoice_ids = fields.One2many(check_company=True)
    move_line_ids = fields.One2many(
        "account.move.line", inverse_name="partner_id", check_company=True
    )
    account_analytic_line_ids = fields.One2many(
        "account.analytic.line", inverse_name="partner_id", check_company=True
    )
    account_bank_statement_line_ids = fields.One2many(
        "account.bank.statement.line", inverse_name="partner_id", check_company=True
    )
    account_payment_ids = fields.One2many(
        "account.payment", inverse_name="partner_id", check_company=True,
    )
