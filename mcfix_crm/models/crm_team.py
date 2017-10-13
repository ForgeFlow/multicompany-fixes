# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.resource_calendar_id = False

    @api.multi
    @api.constrains('resource_calendar_id', 'company_id')
    def _check_company_resource_calendar_id(self):
        for team in self.sudo():
            if team.company_id and team.resource_calendar_id.company_id and \
                    team.company_id != team.resource_calendar_id.company_id:
                raise ValidationError(
                    _('The Company in the Team and in '
                      'Working Time must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(CrmTeam, self)._check_company_id()
        for rec in self:
            activity_report = self.env['crm.activity.report'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if activity_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Team is assigned to Activity Report '
                      '%s.' % activity_report.name))
            opportunity_report = self.env['crm.opportunity.report'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if opportunity_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Team is assigned to Opportunity Report '
                      '%s.' % opportunity_report.name))
            lead = self.env['crm.lead'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if lead:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sales Team is assigned to Lead '
                      '%s.' % lead.name))
