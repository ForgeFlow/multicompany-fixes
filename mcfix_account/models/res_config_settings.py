from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ResConfigSettings, self)._onchange_company_id()
        if self.company_id and self.chart_template_id.company_id and \
                self.chart_template_id.company_id != self.company_id:
            self.chart_template_id = self.company_id.chart_template_id
        if self.company_id and self.default_sale_tax_id.company_id and \
                self.default_sale_tax_id.company_id != self.company_id:
            self.default_sale_tax_id = False
        if self.company_id and self.default_purchase_tax_id.company_id and \
                self.default_purchase_tax_id.company_id != self.company_id:
            self.default_purchase_tax_id = False

    @api.multi
    @api.constrains('company_id', 'tax_cash_basis_journal_id')
    def _check_company_id_tax_cash_basis_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_cash_basis_journal_id.company_id and\
                    rec.company_id != rec.tax_cash_basis_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'currency_exchange_journal_id')
    def _check_company_id_currency_exchange_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.currency_exchange_journal_id.company_id \
                    and rec.company_id != rec.currency_exchange_journal_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'chart_template_id')
    def _check_company_id_chart_template_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.chart_template_id.company_id and\
                    rec.company_id != rec.chart_template_id.company_id:
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Chart Template must be the same.'))
