# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAnalyticAccount, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('project_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      ' is assigned to Sales Order '
                      '%s.' % order.name))
            order = self.env['sale.order'].search(
                [('related_project_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Sales Order '
                      '%s.' % order.name))
