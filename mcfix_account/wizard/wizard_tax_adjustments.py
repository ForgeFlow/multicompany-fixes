from odoo import models, fields, api


class TaxAdjustments(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, default=False,
                                 domain=[('type', '=', 'general')])
    company_currency_id = fields.Many2one(default=False,
                                          compute='_get_currency')

    @api.depends('company_id')
    @api.one
    def _get_currency(self):
        self.company_currency_id = self.company_id.currency_id
        self.debit_account_id = False
        self.credit_account_id = False
        self.journal_id = False
        self.tax_id = False
