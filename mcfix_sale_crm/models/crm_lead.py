# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(CrmLead, self).onchange_company_id()
        self.order_ids = False

    @api.multi
    @api.constrains('order_ids', 'company_id')
    def _check_company_order_ids(self):
        for lead in self.sudo():
            for sale_order in lead.order_ids:
                if lead.company_id and sale_order.company_id and \
                        lead.company_id != sale_order.company_id:
                    raise ValidationError(
                        _('The Company in the Lead and in '
                          'Sales Order must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(CrmLead, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('opportunity_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Lead is assigned to Sales Order '
                      '%s.' % order.name))
