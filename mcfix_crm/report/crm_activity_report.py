# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(CrmActivityReport, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.team_id = False
        self.lead_id = False

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_company_team_id(self):
        for activity_report in self.sudo():
            if activity_report.company_id and activity_report.team_id.\
                    company_id and activity_report.company_id != \
                    activity_report.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Activity Report and in '
                      'Team must be the same.'))
        return True

    @api.multi
    @api.constrains('lead_id', 'company_id')
    def _check_company_lead_id(self):
        for activity_report in self.sudo():
            if activity_report.company_id and activity_report.lead_id.\
                    company_id and activity_report.company_id != \
                    activity_report.lead_id.company_id:
                raise ValidationError(
                    _('The Company in the Activity Report and in '
                      'Lead must be the same.'))
        return True
