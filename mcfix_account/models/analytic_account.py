# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAnalyticAccount, self)._check_company_id()
        for rec in self:
            move_line = self.env['account.move.line'].search(
                [('analytic_account_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Move Line '
                      '%s of Move %s.' % (move_line.name,
                                          move_line.move_id.name)))
            invoice_line = self.env['account.invoice.line'].search(
                [('account_analytic_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Invoice Line '
                      '%s of Invoice %s.' % (invoice_line.name,
                                             invoice_line.invoice_id.name)))
            invoice_tax = self.env['account.invoice.tax'].search(
                [('account_analytic_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_tax:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic account is assigned to Invoice Tax '
                      '%s.' % invoice_tax.name))
            reconcile_model = self.env['account.reconcile.model'].search(
                [('analytic_account_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if reconcile_model:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Reconcile Model '
                      '%s.' % reconcile_model.name))
            reconcile_model = self.env['account.reconcile.model'].search(
                [('second_analytic_account_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if reconcile_model:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Reconcile Model '
                      '%s.' % reconcile_model.name))
