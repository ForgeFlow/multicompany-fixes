from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(AccountInvoice, self.with_context(
            force_company=self.company_id.id
        ))._onchange_company_id()
        if self.company_id and self.partner_shipping_id.company_id and \
                self.partner_shipping_id.company_id != self.company_id:
            self.partner_shipping_id = False
            if self.refund_invoice_id.partner_shipping_id:
                self.partner_shipping_id = self.refund_invoice_id.\
                    partner_shipping_id
            else:
                self.partner_shipping_id = False
        if self.company_id and self.team_id.company_id and \
                self.team_id.company_id != self.company_id:
            self.team_id = False

    @api.multi
    @api.constrains('company_id', 'partner_shipping_id')
    def _check_company_id_partner_shipping_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_shipping_id.company_id and\
                    rec.company_id != rec.partner_shipping_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'team_id')
    def _check_company_id_team_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.team_id.company_id and\
                    rec.company_id != rec.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Crm Team must be the same.'))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id', 'sale_line_ids')
    def _check_company_id_sale_line_ids(self):
        for rec in self.sudo():
            for line in rec.sale_line_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Invoice Line and in '
                          'Sale Order Line (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountInvoiceLine, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['sale.order.line'].search(
                    [('invoice_lines', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice Line is assigned to '
                          'Sale Order Line (%s).' % field.name_get()[0][1]))
