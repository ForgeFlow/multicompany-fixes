# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    company_id = fields.Many2one(readonly=False)

    @api.constrains('company_id', 'profile_id')
    def _check_company_id_profile_id(self):
        for rec in self.sudo():
            if not rec.profile_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Account Asset Profile must be the same.'))

    @api.constrains('company_id', 'parent_id')
    def _check_company_id_parent_id(self):
        for rec in self.sudo():
            if not rec.parent_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Account Asset parent must be the same.'))

    @api.constrains('company_id', 'child_ids')
    def _check_company_id_child_ids(self):
        for rec in self.sudo():
            if not rec.child_ids.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Account Asset childs must be the same.'))

    @api.constrains('company_id', 'account_move_line_ids')
    def _check_company_id_account_move_line_ids(self):
        for rec in self.sudo():
            if not rec.account_move_line_ids.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Account Move lines must be the same.'))

    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Partner must be the same.'))

    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset and in '
                      'Account Analytic Account must be the same.'))


class AccountAssetLine(models.Model):
    _inherit = 'account.asset.line'

    company_id = fields.Many2one(
        'res.company',
        store=True,
        readonly=True,
        related='asset_id.company_id',
    )

    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if not rec.move_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Line and in '
                      'Account Move must be the same.'))
