# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ProcurementRule, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            order = self.env['procurement.order'].search(
                [('rule_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Rule is assigned to Procurement Order '
                      '%s.' % order.name))


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ProcurementOrder, self).name_get()
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
        self.rule_id = False

    @api.multi
    @api.constrains('rule_id', 'company_id')
    def _check_company_rule_id(self):
        for order in self.sudo():
            if order.company_id and order.rule_id.company_id and \
                    order.company_id != order.rule_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Procurement Rule must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        pass
