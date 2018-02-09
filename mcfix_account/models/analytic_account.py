from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountAnalyticAccount, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice.line'].search(
                    [('account_analytic_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Invoice Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.invoice.tax'].search(
                    [('account_analytic_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Invoice Tax (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('second_analytic_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Reconcile Model (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('analytic_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Reconcile Model (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('analytic_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Move Line (%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.report'].search(
                    [('account_analytic_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Analytic Account is assigned to '
                          'Account Invoice Report (%s)'
                          '.' % field.name_get()[0][1]))


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.move_id.company_id and\
                    rec.company_id != rec.move_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Account Move Line must be the same.'))

    @api.multi
    @api.constrains('company_id', 'general_account_id')
    def _check_company_id_general_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.general_account_id.company_id and\
                    rec.company_id != rec.general_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Account Account must be the same.'))
