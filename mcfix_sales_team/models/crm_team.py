# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(CrmTeam, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        team = super(CrmTeam, self)._get_default_team_id(user_id=user_id)
        if team:
            forced_company_id = self.env.context.get('force_company', False)
            if forced_company_id and team.company_id.id != forced_company_id:
                team = self.env['crm.team'].sudo().search([
                    '|', ('user_id', '=', user_id),
                    ('member_ids', '=', user_id),
                    '|', ('company_id', '=', False),
                    ('company_id', '=', forced_company_id)
                ], limit=1)
        return team
