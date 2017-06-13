# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if rec.company_id:
                orders = self.env['sale.order'].search(
                    [('team_id', '=', rec.id), ('company_id', '!=',
                                                rec.company_id.id)])
                if orders:
                    raise ValidationError(_('Sales orders already exist '
                                            'referencing this team in other '
                                            'companies.'))
