# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        ''' Fix to cover the scenario where a user is assigned to a sales
        team of another company that he does not have permissions on '''
        team = super(CrmTeam, self)._get_default_team_id(user_id=user_id)
        team = self.search([('id', '=', team.id)])
        return team
