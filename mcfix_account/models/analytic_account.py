from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res = res + [
            self.env['account.invoice.line'].search(
                [('account_analytic_id', '=', self.id)]),
            self.env['account.invoice.tax'].search(
                [('account_analytic_id', '=', self.id)]),
            self.env['account.reconcile.model'].search(
                [('second_analytic_account_id', '=', self.id)]),
            self.env['account.reconcile.model'].search(
                [('analytic_account_id', '=', self.id)]),
            self.env['account.move.line'].search(
                [('analytic_account_id', '=', self.id)]),
        ]
        return res


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
