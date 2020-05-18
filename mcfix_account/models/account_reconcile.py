from odoo import api, fields, models


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"
    _check_company_auto = True

    debit_move_id = fields.Many2one(check_company=True)
    credit_move_id = fields.Many2one(check_company=True)

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.move', [('tax_cash_basis_rec_id', '=', self.id)]),
        ]
        return res


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"
    _check_company_auto = True

    match_journal_ids = fields.Many2many(
        domain="[('type', 'in', ('bank', 'cash')),"
               " ('company_id', '=', company_id)]",
        check_company=True)
    match_partner_ids = fields.Many2many(check_company=True)
    account_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    journal_id = fields.Many2one(check_company=True)
    tax_ids = fields.Many2many(check_company=True)
    analytic_account_id = fields.Many2one(check_company=True)
    analytic_tag_ids = fields.Many2many(check_company=True)
    second_account_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    second_journal_id = fields.Many2one(check_company=True)
    second_tax_ids = fields.Many2many(check_company=True)
    second_analytic_account_id = fields.Many2one(check_company=True)
    second_analytic_tag_ids = fields.Many2many(check_company=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        # if not self.tax_ids.check_company(self.company_id):
        #     self.tax_id = False
        if not self.account_id.check_company(self.company_id):
            self.account_id = False
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = False
        if not self.analytic_account_id.check_company(self.company_id):
            self.analytic_account_id = False
    #     if not self.second_tax_id.check_company(self.company_id):
    #         self.second_tax_id = False
    #     if not self.second_account_id.check_company(self.company_id):
    #         self.second_account_id = False
    #     if not self.second_journal_id.check_company(self.company_id):
    #         self.second_journal_id = False
    #     if not self.second_analytic_account_id.check_company(self.company_id):
    #         self.second_analytic_account_id = False
