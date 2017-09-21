# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        res = super(SaleOrder, self)._default_warehouse_id()
        if self.env.context.get('force_company', False):
            company = self.env.context.get('force_company')
            warehouse_ids = self.env['stock.warehouse'].search(
                [('company_id', '=', company)], limit=1)
            return warehouse_ids
        return res

    warehouse_id = fields.Many2one(default=_default_warehouse_id)

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        if 'company_id' in rec and rec['company_id']:
            warehouse_id = self.env['stock.warehouse'].search(
                [('company_id', '=', rec['company_id'])], limit=1)
            if warehouse_id:
                rec.update({
                    'warehouse_id': warehouse_id.id})
        return rec

    @api.onchange('team_id')
    def onchange_team_id_change_warehouse(self):
        super(SaleOrder, self).onchange_team_id()
        if self.team_id and self.team_id.company_id:
            warehouse_id = self.env['stock.warehouse'].search(
                [('company_id', '=', self.team_id.company_id.id)], limit=1)
            if warehouse_id:
                self.warehouse_id = warehouse_id

    @api.onchange('company_id')
    def onchange_company_id(self):
        res = super(SaleOrder, self).onchange_company_id()
        warehouse_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if warehouse_id:
            self.warehouse_id = warehouse_id
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id and self.warehouse_id.company_id:
            self.company_id = self.warehouse_id.company_id

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_warehouse_company(self):
        for rec in self.sudo():
            if (rec.warehouse_id and rec.warehouse_id.company_id and
                    rec.warehouse_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the warehouse '
                                        'must match with that of the '
                                        'Quotation/Sales Order.'))
