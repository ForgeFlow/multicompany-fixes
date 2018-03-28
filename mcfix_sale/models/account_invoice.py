from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(AccountInvoice, self.with_context(
            force_company=self.company_id.id
        ))._onchange_company_id()
        if not self.partner_shipping_id.check_company(self.company_id):
            self.partner_shipping_id = False
            if self.refund_invoice_id.partner_shipping_id:
                self.partner_shipping_id = self.refund_invoice_id.\
                    partner_shipping_id
            else:
                self.partner_shipping_id = False
        if not self.team_id.check_company(self.company_id):
            self.team_id = False

    @api.multi
    @api.constrains('company_id', 'partner_shipping_id')
    def _check_company_id_partner_shipping_id(self):
        for rec in self.sudo():
            if not rec.partner_shipping_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'team_id')
    def _check_company_id_team_id(self):
        for rec in self.sudo():
            if not rec.team_id.check_company(rec.company_id):
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
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Invoice Line and in '
                          'Sale Order Line (%s) must be the same.'
                          ) % line.name_get()[0][1])

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.sale_line_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order.line', [('invoice_lines', 'in', self.ids)]),
        ]
        return res
