# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountInvoiceReport, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.payment_term_id = False
        self.fiscal_position_id = False
        self.journal_id = False
        self.account_id = False
        self.account_line_id = False

    @api.multi
    @api.constrains('payment_term_id', 'company_id')
    def _check_company_payment_term_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.payment_term_id.\
                    company_id and invoice_report.company_id != \
                    invoice_report.payment_term_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Payment Term must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.fiscal_position_id\
                    .company_id and invoice_report.company_id != \
                    invoice_report.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Fiscal Position must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.journal_id.\
                    company_id and invoice_report.company_id != invoice_report\
                    .journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.account_id.\
                    company_id and invoice_report.company_id != invoice_report\
                    .account_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('account_line_id', 'company_id')
    def _check_company_account_line_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.account_line_id.\
                    company_id and invoice_report.company_id != invoice_report\
                    .account_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Account Line must be the same.'))
        return True
