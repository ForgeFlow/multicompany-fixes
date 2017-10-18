# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountMove, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            order = self.env['pos.order'].sudo().search(
                [('account_move', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal Entry is assigned to Pos Order '
                      '%s.' % order.name))
