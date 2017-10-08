# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAccount, self)._check_company_id()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                template = self.env['product.template'].search(
                    [('property_account_creditor_price_difference', '=',
                      rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if template:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'account is assigned to Product Template '
                          '%s.' % template.name))
