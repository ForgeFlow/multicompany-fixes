from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for rec in self:
            if (
                rec.partner_id and not rec.invoice_ids and
                rec.payment_type != 'transfer'
            ):
                if rec.partner_type == 'customer':
                    rec.destination_account_id = rec.partner_id.with_context(
                        force_company=rec.company_id.id
                    ).property_account_receivable_id.id
                else:
                    rec.destination_account_id = rec.partner_id.with_context(
                        force_company=rec.company_id.id
                    ).property_account_payable_id.id

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

    @api.model_create_multi
    def create(self, mvals):
        for vals in mvals:
            if 'company_id' not in vals:
                journal_id = vals.get('journal_id')
                journal = self.env['account.journal'].browse(journal_id)
                vals['company_id'] = journal.company_id.id
        return super(AccountPayment, self).create(mvals)

    @api.multi
    @api.constrains('journal_id', 'destination_journal_id')
    def _check_company_id_destination_journal_id(self):
        for rec in self.sudo():
            if not rec.destination_journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('journal_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('journal_id')
    def _check_company_id_destination_account_id(self):
        for rec in self.sudo():
            if not rec.destination_account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('journal_id', 'invoice_ids')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Payment and in '
                          'Account Invoice (%s) must be the same'
                          '.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('journal_id', 'writeoff_account_id')
    def _check_company_id_writeoff_account_id(self):
        for rec in self.sudo():
            if not rec.writeoff_account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Account Journal must be the same.'))

    @api.constrains('journal_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_ids, self.move_line_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.invoice', [('payment_ids', 'in', self.ids)]),
        ]
        return res
