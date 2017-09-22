# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    company_id = fields.Many2one(store=True, readonly=False,
                                 related=False, required=True)

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
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
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

    @api.onchange('payment_type', 'company_id')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        res['domain']['journal_id'].append(('company_id', '=',
                                            self.company_id.id))
        return res

    @api.model
    def create(self, vals):
        if 'company_id' not in vals:
            journal_id = vals.get('journal_id')
            journal = self.env['account.journal'].browse(journal_id)
            vals['company_id'] = journal.company_id.id
        return super(AccountPayment, self).create(vals)
