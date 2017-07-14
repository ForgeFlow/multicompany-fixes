# -*- coding: utf-8 -*-
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
                                          compute='_compute_currency')

    @api.multi
    @api.depends('company_id')
    def _compute_currency(self):
        for tax in self:
            tax.company_currency_id = tax.company_id.currency_id
            tax.debit_account_id = False
            tax.credit_account_id = False
            tax.journal_id = False
            tax.tax_id = False
