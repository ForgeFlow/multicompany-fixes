# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountFiscalPosition, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            order = self.env['pos.order'].search(
                [('fiscal_position_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Fiscal Position is assigned to Pos Order '
                      '%s.' % order.name))
            config = self.env['pos.config'].search(
                [('fiscal_position_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Fiscal Position is assigned to Pos Config '
                      '%s.' % config.name))
            config = self.env['pos.config'].search(
                [('default_fiscal_position_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Default Fiscal Position is assigned to Pos Config '
                      '%s.' % config.name))
