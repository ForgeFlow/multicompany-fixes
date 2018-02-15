# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountPaymentTerm, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            invoice = self.env['account.invoice'].search(
                [('payment_term_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Payment Term is assigned to Invoice '
                      '%s.' % invoice.name))
            invoice_report = self.env['account.invoice.report'].search(
                [('payment_term_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Payment Terms is assigned to Invoice Report '
                      '%s.' % invoice_report.name))
            partner = self.env['res.partner'].search(
                [('property_payment_term_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if partner:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Customer Payment Term is assigned to Partner '
                      '%s.' % partner.name))
            partner = self.env['res.partner'].search(
                [('property_supplier_payment_term_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if partner:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Vendor Payment Term is assigned to Partner '
                      '%s.' % partner.name))


class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.multi
    def _get_default_company(self):
        if self.env.context.get('default_invoice_ids'):
            inv = self.env['account.invoice'].browse(self.env.context['default_invoice_ids'][0][1])
            return inv.company_id.id
        return self.env.user.company_id.id

    create_company_id = fields.Many2one('res.company', string='Company', default=_get_default_company)

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountAbstractPayment, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

#     @api.onchange('create_company_id')
#     def onchange_company_id(self):
#         if self.create_company_id and self.journal_id.company_id != self.create_company_id:
#             self.journal_id = False

    # Company is related from journal_id cannot be different!!!!!
    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for abstract_payment in self.sudo():
            if abstract_payment.company_id and abstract_payment.journal_id.\
                    company_id and abstract_payment.company_id != \
                    abstract_payment.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Payment and in '
                      'Payment Journal must be the same.'))
        return True


class AccountRegisterPayment(models.TransientModel):
    _inherit = 'account.register.payments'

    @api.model
    def default_get(self, fields):
        rec = super(AccountRegisterPayment, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        invoices = self.env[active_model].browse(active_ids)
        if invoices:
            rec['create_company_id'] = invoices[0].company_id.id
        return rec

    @api.onchange('create_company_id')
    def onchange_company_id(self):
        if self.create_company_id and \
                self.journal_id.company_id != self.create_company_id:
            self.journal_id = False


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountPayment, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for rec in self:
            if (
                self.partner_id and not rec.invoice_ids and
                self.payment_type != 'transfer'
            ):
                if self.partner_type == 'customer':
                    self.destination_account_id = \
                        self.partner_id.with_context(
                            force_company=rec.company_id.id).\
                        property_account_receivable_id.id
                else:
                    self.destination_account_id = self.partner_id.with_context(
                        force_company=rec.company_id.id).\
                        property_account_payable_id.id

    @api.onchange('create_company_id')
    def onchange_company_id(self):
        if self.create_company_id and \
                self.journal_id.company_id != self.create_company_id:
            self.journal_id = False
        if self.create_company_id:
            return self._onchange_payment_type()

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        res['domain']['journal_id'].append(('company_id', '=',
                                            self.create_company_id.id))
        return res

    # is related!!!
#     @api.model
#     def create(self, vals):
#         if 'company_id' not in vals:
#             journal_id = vals.get('journal_id')
#             journal = self.env['account.journal'].browse(journal_id)
#             vals['company_id'] = journal.company_id.id
#         return super(AccountPayment, self).create(vals)
