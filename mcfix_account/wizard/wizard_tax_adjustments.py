from odoo import fields, api, models


class TaxAdjustments(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one(default=False, check_company=True)
    company_currency_id = fields.Many2one(
        default=False,
        compute='_compute_currency', store=True)
    debit_account_id = fields.Many2one(check_company=True)
    credit_account_id = fields.Many2one(check_company=True)

    @api.depends('company_id')
    def _compute_currency(self):
        for tax in self:
            tax.company_currency_id = tax.company_id.currency_id
            tax.debit_account_id = False
            tax.credit_account_id = False
            tax.journal_id = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.debit_account_id.check_company(self.company_id):
            self.debit_account_id = False
        if not self.credit_account_id.check_company(self.company_id):
            self.credit_account_id = False
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = False
