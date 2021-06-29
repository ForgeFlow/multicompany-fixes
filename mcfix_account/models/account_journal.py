from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountJournalGroup(models.Model):
    _inherit = "account.journal.group"
    _check_company_auto = True

    excluded_journal_ids = fields.Many2many(check_company=True)


class AccountJournal(models.Model):
    _inherit = "account.journal"
    _check_company_auto = True

    account_control_ids = fields.Many2many(check_company=True)
    default_credit_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
    default_debit_account_id = fields.Many2one(check_company=True)
    profit_account_id = fields.Many2one(check_company=True)
    loss_account_id = fields.Many2one(check_company=True)
    bank_account_id = fields.Many2one(check_company=True)
    journal_group_ids = fields.Many2many(check_company=True)
    secure_sequence_id = fields.Many2one(check_company=True)

    def action_open_reconcile(self):
        if self.type in ["bank", "cash"]:
            if len(self.mapped("company_id").ids) > 1:
                raise UserError(_("All journals should be of the same company."))
        return super(AccountJournal, self).action_open_reconcile()

    @api.depends("company_id")
    def name_get(self):
        names = super(AccountJournal, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.profit_account_id.check_company(self.company_id):
            self.profit_account_id = False
        if not self.loss_account_id.check_company(self.company_id):
            self.loss_account_id = False
        if not self.account_control_ids.check_company(self.company_id):
            self.account_control_ids = self.account_control_ids.filtered(
                lambda a: a.company_id == self.company_id or not a.company_id
            )
        if not self.default_debit_account_id.check_company(self.company_id):
            self.default_debit_account_id.company_id = self.company_id
        if not self.default_credit_account_id.check_company(self.company_id):
            self.default_credit_account_id.company_id = self.company_id
        if not self.sequence_id.check_company(self.company_id):
            self.sequence_id.company_id = self.company_id

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("account.bank.statement", [("journal_id", "=", self.id)]),
            ("account.bank.statement.line", [("journal_id", "=", self.id)]),
            ("account.move", [("journal_id", "=", self.id)]),
            ("account.move.line", [("journal_id", "=", self.id)]),
            ("account.payment", [("destination_journal_id", "=", self.id)]),
            ("account.payment", [("journal_id", "=", self.id)]),
            ("account.reconcile.model", [("journal_id", "=", self.id)]),
            ("account.reconcile.model", [("second_journal_id", "=", self.id)]),
        ]
        return res
