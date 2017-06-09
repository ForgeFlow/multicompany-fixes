from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.onchange('company_id')
    def change_company(self):
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
        self.fiscal_position_id = \
            self.env['account.fiscal.position'].with_context(
            force_company=self.company_id.id).get_fiscal_position(
                self.partner_id.id, delivery_id=addr['delivery'])

    @api.multi
    def action_account_invoice_payment(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_invoice_payment')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_id': action.view_id.id,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            "context": {'default_invoice_ids': [(4, self.id, None)],
                        'default_company_id': self.company_id.id}
        }


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        return super(AccountInvoiceLine, self.with_context(force_company=company.id)).get_invoice_line_account(
            type, product, fpos, company)
        # accounts = product.product_tmpl_id.with_context(force_company=company.id).get_product_accounts(fpos)
        # if type in ('out_invoice', 'out_refund'):
        #    return accounts['income']
        # return accounts['expense']

    @api.model
    def change_company_id(self):
        part = self.invoice_id.partner_id
        type = self.invoice_id.type
        company = self.invoice_id.company_id.id
        if part.lang:
            product = self.product_id.with_context(lang=part.lang)
        else:
            product = self.product_id
        account = self.get_invoice_line_account(
            type,
            product.with_context(force_company=company),
            self.invoice_id.fiscal_position_id,
            self.invoice_id.company_id)
        if account:
            self.account_id = account.id
        self._set_taxes()
