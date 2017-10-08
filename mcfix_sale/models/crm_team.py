# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(CrmTeam, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Team is assigned to Sales Order '
                      '%s.' % order.name))
            report = self.env['sale.report'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Team is assigned to Report '
                      '%s.' % report.name))
            invoice = self.env['account.invoice'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sales Team is assigned to Invoice '
                      '%s.' % invoice.name))
            invoice_report = self.env['account.invoice.report'].search(
                [('team_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sales Team is assigned to Invoice Report '
                      '%s.' % invoice_report.name))
