from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class TaxAdjustments(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one(default=False)
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

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.debit_account_id.company_id and \
                self.debit_account_id.company_id != self.company_id:
            self.debit_account_id = False
        if self.company_id and self.credit_account_id.company_id and \
                self.credit_account_id.company_id != self.company_id:
            self.credit_account_id = False
        if self.company_id and self.tax_id.company_id and \
                self.tax_id.company_id != self.company_id:
            self.tax_id = False
        if self.company_id and self.journal_id.company_id and \
                self.journal_id.company_id != self.company_id:
            self.journal_id = False

    @api.multi
    @api.constrains('company_id', 'debit_account_id')
    def _check_company_id_debit_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.debit_account_id.company_id and\
                    rec.company_id != rec.debit_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Tax Adjustments Wizard and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'credit_account_id')
    def _check_company_id_credit_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.credit_account_id.company_id and\
                    rec.company_id != rec.credit_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Tax Adjustments Wizard and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_id')
    def _check_company_id_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_id.company_id and\
                    rec.company_id != rec.tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Tax Adjustments Wizard and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Tax Adjustments Wizard and in '
                      'Account Journal must be the same.'))
