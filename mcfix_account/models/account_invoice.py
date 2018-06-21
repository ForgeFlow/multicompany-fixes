from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountInvoice, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        company_id = self.company_id.id
        addr = self.partner_id.address_get(['delivery'])
        self.fiscal_position_id = self.env['account.fiscal.position']. \
            with_context(force_company=company_id). \
            get_fiscal_position(self.partner_id.id,
                                delivery_id=addr['delivery'])
        domain = {}
        p = self.partner_id if not company_id else \
            self.partner_id.with_context(force_company=company_id)
        if self.type in ('in_invoice', 'out_refund'):
            bank_ids = p.commercial_partner_id.bank_ids.filtered(
                lambda b: b.company_id.id == company_id or not b.company_id)
            bank_id = bank_ids[0].id if bank_ids else False
            self.partner_bank_id = bank_id
            domain = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}
        if domain:
            res['domain'] = domain
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self._cache.update(self._convert_to_cache(
                {'partner_id': False}, update=True))
        if not self.refund_invoice_id.check_company(self.company_id):
            self.refund_invoice_id = False
        if not self.payment_term_id.check_company(self.company_id):
            if self.refund_invoice_id.payment_term_id:
                self.payment_term_id = self.refund_invoice_id.payment_term_id
            else:
                self.payment_term_id = False
        if not self.fiscal_position_id.check_company(self.company_id):
            if self.refund_invoice_id.fiscal_position_id:
                self.fiscal_position_id = \
                    self.refund_invoice_id.fiscal_position_id
            else:
                self.fiscal_position_id = False
        if not self.move_id.check_company(self.company_id):
            if self.refund_invoice_id.move_id:
                self.move_id = self.refund_invoice_id.move_id
            else:
                self.move_id = False
        if not self.account_id.check_company(self.company_id):
            if self.refund_invoice_id.account_id:
                self.account_id = self.refund_invoice_id.account_id
            else:
                self._cache.update(self._convert_to_cache(
                    {'account_id': False}, update=True))
        if not self.partner_bank_id.check_company(self.company_id):
            if self.refund_invoice_id.partner_bank_id:
                self.partner_bank_id = self.refund_invoice_id.partner_bank_id
            else:
                self.partner_bank_id = False
        if self.company_id and self.payment_ids:
            self.payment_ids = self.env['account.payment'].search(
                [('invoice_ids', 'in', [self.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', self.company_id.id)])
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = self.env['account.journal'].search(
                [('company_id', '=', self.company_id.id),
                 ('type', '=', self.journal_id.type)
                 ], limit=1)
        for line in self.invoice_line_ids:
            line.change_company_id()

    @api.multi
    @api.constrains('company_id', 'payment_term_id')
    def _check_company_id_payment_term_id(self):
        for rec in self.sudo():
            if not rec.payment_term_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Payment Term must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if not rec.fiscal_position_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'payment_ids')
    def _check_company_id_payment_ids(self):
        for rec in self.sudo():
            for line in rec.payment_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Invoice and in '
                          'Account Payment (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'refund_invoice_id')
    def _check_company_id_refund_invoice_id(self):
        for rec in self.sudo():
            if not rec.refund_invoice_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if not rec.move_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if not rec.account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_bank_id')
    def _check_company_id_partner_bank_id(self):
        for rec in self.sudo():
            if not rec.partner_bank_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Res Partner Bank must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.refund_invoice_ids,
            self.invoice_line_ids,
            self.tax_line_ids,
            self.move_id,
            self.payment_ids,
        ]
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.company_id = self.invoice_id.company_id
        res = super()._onchange_product_id()
        self.change_company_id()
        return res

    @api.onchange('account_id')
    def onchange_account_id(self):
        return self.with_context(
            force_company=self.invoice_id.company_id.id
        )._onchange_account_id()

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
        if not self.account_analytic_id.check_company(self.company_id):
            self.account_analytic_id = self.get_default_account_analytic()
        self.with_context(company_id=company_id)._set_taxes()

    def get_default_account_analytic(self):
        return False

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        return super(AccountInvoiceLine, self.with_context(
            force_company=company.id)).get_invoice_line_account(
            type, product, fpos, company)

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_line_tax_ids')
    def _check_company_id_invoice_line_tax_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_line_tax_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Invoice Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if not rec.invoice_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if not rec.account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Account must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    @api.multi
    @api.constrains('company_id', 'tax_id')
    def _check_company_id_tax_id(self):
        for rec in self.sudo():
            if not rec.tax_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if not rec.invoice_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if not rec.account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Tax and in '
                      'Account Analytic Account must be the same.'))
