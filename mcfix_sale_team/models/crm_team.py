# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        team = super(CrmTeam, self)._get_default_team_id(user_id=user_id)
        team = self.search([('id', '=', team.id)])
        forced_company_id = self.env.context.get('force_company', False)
        if forced_company_id and team.company_id.id != forced_company_id:
            team = self.env['crm.team'].sudo().search([
                '|', ('user_id', '=', user_id), ('member_ids', '=', user_id),
                '|', ('company_id', '=', False),
                ('company_id', '=', forced_company_id)
            ], limit=1)
        return team
