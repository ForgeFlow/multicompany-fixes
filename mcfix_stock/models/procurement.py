# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProcurementRule, self)._check_company_id()
        self.location_id = False
        self.location_src_id = False
        self.route_id = False
        self.warehouse_id = False
        self.propagate_warehouse_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.location_id and \
                    rule.company_id != rule.location_id.company_id:
                raise ValidationError(_('The Company in the Procurement Rule '
                                        'and in Location must be the same.'))
        return True

    @api.multi
    @api.constrains('location_src_id', 'company_id')
    def _check_company_location_src_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.location_src_id and \
                    rule.company_id != rule.location_src_id.company_id:
                raise ValidationError(_('The Company in the Procurement Rule '
                                        'and in Location must be the same.'))
        return True

    @api.multi
    @api.constrains('route_id', 'company_id')
    def _check_company_route_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.route_id and \
                    rule.company_id != rule.route_id.company_id:
                raise ValidationError(_('The Company in the Procurement Rule '
                                        'and in Route must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.warehouse_id and \
                    rule.company_id != rule.warehouse_id.company_id:
                raise ValidationError(_('The Company in the Procurement Rule '
                                        'and in Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('propagate_warehouse_id', 'company_id')
    def _check_company_propagate_warehouse_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.propagate_warehouse_id and \
                    rule.company_id != rule.propagate_warehouse_id.company_id:
                raise ValidationError(_('The Company in the Procurement Rule '
                                        'and in Warehouse must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProcurementRule, self)._check_company_id()
        for rec in self:
            location_route = self.env['stock.location.route'].search(
                [('pull_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location_route:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Rule is assigned to Location Route '
                      '%s.' % location_route.name))
            warehouse = self.env['stock.warehouse'].search(
                [('mto_pull_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Rule is assigned to Warehouse '
                      '%s.' % warehouse.name))
