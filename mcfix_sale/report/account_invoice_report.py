# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountInvoiceReport, self).onchange_company_id()
        self.team_id = False

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_company_team_id(self):
        for invoice_report in self.sudo():
            if invoice_report.company_id and invoice_report.team_id.company_id\
                    and invoice_report.company_id != invoice_report.team_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Invoice Report and in '
                      'Sales Team must be the same.'))
        return True
