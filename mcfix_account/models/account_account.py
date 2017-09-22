# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountAccount, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.constrains('tax_ids', 'company_id')
    def _check_company_tax_ids(self):
        for account in self.sudo():
            for tax in account.tax_ids:
                if account.company_id != tax.company_id:
                    raise ValidationError(_('The Company in the Account and '
                                            'in tax %s must be the same.' %
                                            tax.name))
        return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.tax_ids = False

    def write(self, vals):
        if vals.get('company_id', False):
            if not self.env.context.get('bypass_company_validation', False):
                for rec in self:
                    journal = self.env['account.journal'].search(
                        [('default_debit_account_id', '=', rec.id),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if journal:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'account is assigned as Debit Account in '
                              'Account Journal %s.' % journal.name))

                    journal = self.env['account.journal'].search(
                        [('default_credit_account_id', '=', rec.id),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if journal:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'account is assigned as Credit Account '
                              'in Account Journal %s.' % journal.name))

                    journal = self.env['account.journal'].search(
                        [('profit_account_id', '=', rec.id),
                         ('company_id', '!=', vals['company_id'])], limit=1)

                    if journal:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'account is assigned as Profit Account in '
                              'Account Journal %s.' % journal.name))

                    journal = self.env['account.journal'].search(
                        [('loss_account_id', '=', rec.id),
                         ('company_id', '!=', vals['company_id'])], limit=1)

                    if journal:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'account is assigned as Loss Account in '
                              'Account Journal %s.' % journal.name))

        return super(AccountAccount, self).write(vals)
