# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmOpportunityReport(models.Model):
    _inherit = 'crm.opportunity.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(CrmOpportunityReport, self).name_get()
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

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_company_team_id(self):
        for opportunity_report in self.sudo():
            if opportunity_report.company_id and opportunity_report.team_id.\
                    company_id and opportunity_report.company_id != \
                    opportunity_report.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Opportunity Report and in '
                      'Team must be the same.'))
        return True
