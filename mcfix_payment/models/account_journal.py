# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountJournal, self)._check_company_id()
        for rec in self:
            acquirer = self.env['payment.acquirer'].search(
                [('journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if acquirer:
                raise ValidationError(
                    _('You cannot change the company, as this Journal'
                      ' is assigned to Payment Acquirer '
                      '%s.' % acquirer.name))
