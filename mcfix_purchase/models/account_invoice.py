from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(AccountInvoice, self)._onchange_company_id()
        if self.company_id and self.purchase_id.company_id and \
                self.purchase_id.company_id != self.company_id:
            if self.refund_invoice_id.purchase_id:
                self.purchase_id = self.refund_invoice_id.purchase_id
            else:
                self.purchase_id = False

    @api.multi
    @api.constrains('company_id', 'purchase_id')
    def _check_company_id_purchase_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.purchase_id.company_id and\
                    rec.company_id != rec.purchase_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Purchase Order must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountInvoice, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['purchase.order'].search(
                    [('invoice_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Purchase Order '
                          '(%s).' % field.name_get()[0][1]))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id', 'purchase_line_id')
    def _check_company_id_purchase_line_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.purchase_line_id.company_id and\
                    rec.company_id != rec.purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Purchase Order Line must be the same.'))
