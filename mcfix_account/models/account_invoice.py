from odoo import api, models, _
from odoo.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        for invoice in self:
            invoice.journal_id = self.env['account.journal'].search(
                [('company_id', '=', invoice.company_id.id),
                 ('type', '=', invoice.journal_id.type)
                 ], limit=1)
            for line in invoice.invoice_line_ids:
                line.change_company_id()
        return {}

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        addr = self.partner_id.address_get(['delivery'])
        self.fiscal_position_id = self.env['account.fiscal.position'].\
            with_context(force_company=self.company_id.id).\
            get_fiscal_position(self.partner_id.id,
                                delivery_id=addr['delivery'])

    @api.multi
    @api.constrains('payment_term_id', 'company_id')
    def _check_company_payment_term(self):
        for invoice in self:
            if invoice.company_id and invoice.payment_term_id and\
                    invoice.company_id != invoice.payment_term_id.company_id:
                raise Warning(_('The Company in the Invoice and in '
                                'Payment Term must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position(self):
        for invoice in self:
            if invoice.company_id and invoice.fiscal_position_id and\
                    invoice.company_id != invoice.fiscal_position_id.\
                    company_id:
                raise Warning(_('The Company in the Invoice and in '
                                'Fiscal Position must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account(self):
        for invoice in self:
            if invoice.company_id and invoice.account_id and\
                    invoice.company_id != invoice.account_id.company_id:
                raise Warning(_('The Company in the Invoice and in '
                                'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal(self):
        for invoice in self:
            if invoice.company_id and invoice.journal_id and\
                    invoice.company_id != invoice.journal_id.company_id:
                raise Warning(_('The Company in the Invoice and in '
                                'Journal must be the same.'))
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.v8
    def get_invoice_line_account(self, invoice_type, product, fpos, company):
        return super(AccountInvoiceLine, self.with_context(
            force_company=company.id)).get_invoice_line_account(
            invoice_type, product, fpos, company)

    @api.model
    def change_company_id(self):
        part = self.invoice_id.partner_id
        invoice_type = self.invoice_id.type
        company = self.invoice_id.company_id.id
        if part.lang:
            product = self.product_id.with_context(lang=part.lang)
        else:
            product = self.product_id
        account = self.get_invoice_line_account(
            invoice_type,
            product.with_context(force_company=company),
            self.invoice_id.fiscal_position_id,
            self.invoice_id.company_id)
        if account:
            self.account_id = account.id
        self._set_taxes()
