from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountInvoice, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.refund_invoice_id = False
        self.invoice_line_ids = False
        self.tax_line_ids = False
        self.move_id = False
        self.journal_id = False
        self.payment_move_line_ids = False

    @api.multi
    @api.onchange('company_id')
    def _onchange_company_id(self):
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
    @api.constrains('refund_invoice_id', 'company_id')
    def _check_company_refund_invoice_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.refund_invoice_id and \
                    invoice.company_id != invoice.refund_invoice_id.\
                    company_id:
                raise ValidationError(_('The Company in the Invoice and in '
                                        'the Refund must be the same.'))
        return True

    @api.multi
    @api.constrains('payment_term_id', 'company_id')
    def _check_company_payment_term_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.payment_term_id and\
                    invoice.company_id != invoice.payment_term_id.company_id:
                raise ValidationError(_('The Company in the Invoice and in '
                                        'Payment Terms must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position_id(self):
        for invoice in self.sudo():
            if (
                invoice.company_id and
                invoice.fiscal_position_id.company_id and
                invoice.company_id != invoice.fiscal_position_id.company_id
            ):
                raise ValidationError(_('The Company in the Invoice and in '
                                        'Fiscal Position must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for invoice in self.sudo():
            if (
                invoice.company_id and invoice.account_id and
                invoice.company_id != invoice.account_id.company_id
            ):
                raise ValidationError(_('The Company in the Invoice and in '
                                        'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.journal_id and\
                    invoice.company_id != invoice.journal_id.company_id:
                raise ValidationError(_('The Company in the Invoice and in '
                                        'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_line_ids', 'company_id')
    def _check_company_tax_line_ids(self):
        for invoice in self.sudo():
            for tax_line in invoice.tax_line_ids:
                if (
                    invoice.company_id and tax_line.company_id and
                    invoice.company_id != tax_line.company_id
                ):
                    raise ValidationError(
                        _('The Company in the Invoice and in '
                          'Tax Line %s must be the same.') % tax_line.name)
        return True

    @api.multi
    @api.constrains('invoice_line_ids', 'company_id')
    def _check_company_invoice_line_ids(self):
        for invoice in self.sudo():
            for invoice_line in invoice.invoice_line_ids:
                if invoice.company_id and \
                        invoice.company_id != invoice_line.company_id:
                    raise ValidationError(
                        _('The Company in the Invoice and in Invoice Line %s '
                          'must be the same.') % invoice_line.name)
        return True

    @api.multi
    @api.constrains('move_id', 'company_id')
    def _check_company_move_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.move_id and \
                    invoice.company_id != invoice.move_id.company_id:
                raise ValidationError(_('The Company in the Invoice and in '
                                        'Journal Entry must be the same.'))
        return True

    @api.multi
    @api.constrains('payment_move_line_ids', 'company_id')
    def _check_company_payment_move_line_ids(self):
        for invoice in self.sudo():
            for move_line in invoice.payment_move_line_ids:
                if invoice.company_id and \
                        invoice.company_id != move_line.company_id:
                    raise ValidationError(
                        _('The Company in the Invoice and in '
                          'Payment Move Line % must be the same.'
                          ) % move_line.name)
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountInvoiceLine, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.v8
    def get_invoice_line_account(self, invoice_type, product, fpos, company):
        return super(AccountInvoiceLine, self.with_context(
            force_company=company.id)).get_invoice_line_account(
            invoice_type, product, fpos, company)

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.invoice_id = False
        self.account_id = False
        self.invoice_line_tax_ids = False

    @api.model
    def change_company_id(self):
        part = self.invoice_id.partner_id
        invoice_type = self.invoice_id.type
        company_id = self.invoice_id.company_id.id
        if part.lang:
            product = self.product_id.with_context(lang=part.lang)
        else:
            product = self.product_id
        account = self.get_invoice_line_account(
            invoice_type,
            product.with_context(force_company=company_id),
            self.invoice_id.fiscal_position_id,
            self.invoice_id.company_id)
        if account:
            self.account_id = account.id
        self._set_taxes()

    @api.multi
    @api.constrains('invoice_id', 'company_id')
    def _check_company_invoice_id(self):
        for invoice_line in self.sudo():
            if invoice_line.company_id and invoice_line.invoice_id and \
                    invoice_line.company_id != invoice_line.\
                    invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Line and in '
                      'Invoice Reference must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for invoice_line in self.sudo():
            if invoice_line.company_id and invoice_line.account_id and \
                    invoice_line.company_id != invoice_line.\
                    account_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Line and in '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('invoice_line_tax_ids', 'company_id')
    def _check_company_invoice_line_tax_ids(self):
        for invoice_line in self.sudo():
            for invoice_line_tax in invoice_line.invoice_line_tax_ids:
                if invoice_line.company_id and \
                        invoice_line.company_id != invoice_line_tax.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Invoice Line and in Tax %s '
                          'must be the same.') % invoice_line_tax.name)
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            invoice = self.env['account.invoice'].search(
                [('invoice_line_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice Line is assigned to Invoice '
                      '%s.' % invoice.name))


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountInvoiceTax, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.invoice_id = False
        self.tax_id = False
        self.account_id = False

    @api.multi
    @api.constrains('invoice_id', 'company_id')
    def _check_company_invoice_id(self):
        for invoice_tax in self.sudo():
            if invoice_tax.company_id and invoice_tax.invoice_id and \
                    invoice_tax.company_id != invoice_tax.invoice_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Invoice Tax and in '
                      'Invoice must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_id', 'company_id')
    def _check_company_tax_id(self):
        for invoice_tax in self.sudo():
            if invoice_tax.company_id and invoice_tax.tax_id and \
                    invoice_tax.company_id != invoice_tax.tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Tax and in '
                      'Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for invoice_tax in self.sudo():
            if invoice_tax.company_id and invoice_tax.account_id and \
                    invoice_tax.company_id != invoice_tax.account_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Invoice Tax and in '
                      'Tax Account must be the same.'))
        return True
