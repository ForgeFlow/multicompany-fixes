from odoo import fields, models


class SetupBarBankConfigWizard(models.TransientModel):
    _inherit = "account.setup.bank.manual.config"
    _check_company_auto = True

    linked_journal_id = fields.Many2one(check_company=True,)
