# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        account_names = super(AccountAccount, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return account_names
        for account_name in account_names:
            account = self.browse(account_name[0])
            name = "%s [%s]" % (account_name[1], account.company_id.name)
            res += [(account.id, name)]
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
