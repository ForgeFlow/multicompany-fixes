# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.multi
    @api.constrains('company_id')
    def _check_purchase_order_company(self):
        for rec in self:
            if rec.company_id:
                orders = self.env['purchase.order'].search(
                    [('fiscal_position_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if orders:
                    raise ValidationError(_('Purchase Orders already exist '
                                            'referencing this fiscal position '
                                            'in other company : %s.') %
                                          orders.company_id.name)
