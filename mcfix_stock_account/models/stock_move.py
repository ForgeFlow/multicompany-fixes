# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(StockMove, self)._check_company_id()
        for rec in self:
            history = self.env['stock.history'].search(
                [('move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if history:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to History '
                      '%s.' % history.name))
