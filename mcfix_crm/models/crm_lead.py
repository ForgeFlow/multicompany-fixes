# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(CrmLead, self).name_get()
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
        for lead in self.sudo():
            if lead.company_id and lead.team_id.company_id and \
                    lead.company_id != lead.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Lead and in '
                      'Sales Team must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            activity_report = self.env['crm.activity.report'].search(
                [('lead_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if activity_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Lead is assigned to Activity Report '
                      '%s.' % activity_report.name))
