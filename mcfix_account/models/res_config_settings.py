from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ResConfigSettings, self)._onchange_company_id()
        if not self.chart_template_id.check_company(self.company_id):
            self.chart_template_id = self.company_id.chart_template_id
        if not self.default_sale_tax_id.check_company(self.company_id):
            self.default_sale_tax_id = False
        if not self.default_purchase_tax_id.check_company(self.company_id):
            self.default_purchase_tax_id = False

    @api.multi
    @api.constrains('company_id', 'tax_cash_basis_journal_id')
    def _check_company_id_tax_cash_basis_journal_id(self):
        for rec in self.sudo():
            if not rec.tax_cash_basis_journal_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'currency_exchange_journal_id')
    def _check_company_id_currency_exchange_journal_id(self):
        for rec in self.sudo():
            if not rec.currency_exchange_journal_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'chart_template_id')
    def _check_company_id_chart_template_id(self):
        for rec in self.sudo():
            if not rec.chart_template_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Account Chart Template must be the same.'))
