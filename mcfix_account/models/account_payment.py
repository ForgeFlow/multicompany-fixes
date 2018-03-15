from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for rec in self:
            if (self.partner_id and not rec.invoice_ids and
                    self.payment_type != 'transfer'):
                if self.partner_type == 'customer':
                    self.destination_account_id = \
                        self.partner_id.with_context(
                            force_company=rec.company_id.id).\
                        property_account_receivable_id.id
                else:
                    self.destination_account_id = \
                        self.partner_id.with_context(
                            force_company=rec.company_id.id).\
                        property_account_payable_id.id

    @api.onchange('payment_type', 'company_id')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if self.invoice_ids:
            res['domain']['journal_id'].append(
                ('company_id', 'in',
                 self.invoice_ids.mapped('company_id').ids))
        else:
            res['domain']['journal_id'].append(
                ('company_id', '=', self.company_id.id))
        return res

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        journal_type = self.journal_id.type
        super(AccountPayment, self)._onchange_amount()
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        domain_on_types = [('type', 'in', list(journal_types))]

        journal_domain = jrnl_filters['domain'] + domain_on_types
        default_journal_id = self.env.context.get('default_journal_id')
        domain_company = [('company_id', '=', self.env.context.get(
            'default_company_id', self.env.user.company_id.id))]
        if not default_journal_id:
            if journal_type not in journal_types:
                self.journal_id = self.env['account.journal'].search(
                    domain_on_types + domain_company, limit=1)
        else:
            journal_domain = journal_domain.append(
                ('id', '=', default_journal_id))

        return {'domain': {'journal_id': journal_domain}}

    @api.model
    def create(self, vals):
        if 'company_id' not in vals:
            journal_id = vals.get('journal_id')
            journal = self.env['account.journal'].browse(journal_id)
            vals['company_id'] = journal.company_id.id
        return super(AccountPayment, self).create(vals)

    @api.multi
    @api.constrains('company_id', 'destination_journal_id')
    def _check_company_id_destination_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.destination_journal_id.company_id and\
                    rec.company_id != rec.destination_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id')
    def _check_company_id_destination_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.destination_account_id.company_id and\
                    rec.company_id != rec.destination_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_ids')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Payment and in '
                          'Account Invoice (%s) must be the same'
                          '.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'writeoff_account_id')
    def _check_company_id_writeoff_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.writeoff_account_id.company_id and\
                    rec.company_id != rec.writeoff_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('payment_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Payment is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('payment_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Payment is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.multi
    @api.constrains('partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Register Payments and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Register Payments and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('invoice_ids')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Register Payments '
                          'and in Account Invoice (%s) must be '
                          'the same.') % line.name_get()[0][1])
