# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(StockMove, self).onchange_company_id()
        self.purchase_line_id = False

    @api.multi
    @api.constrains('purchase_line_id', 'company_id')
    def _check_company_purchase_line_id(self):
        for move in self.sudo():
            if move.company_id and move.purchase_line_id.company_id and \
                    move.company_id != move.purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Purchase Order Line must be the same.'))
        return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(StockPicking, self).onchange_company_id()
        self.purchase_id = False

    @api.multi
    @api.constrains('purchase_id', 'company_id')
    def _check_company_purchase_id(self):
        for picking in self.sudo():
            if picking.company_id and picking.purchase_id.company_id and \
                    picking.company_id != picking.purchase_id.company_id:
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'Purchase Order must be the same.'))
        return True


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.multi
    def _get_buy_pull_rule(self):
        res = super(StockWarehouse, self)._get_buy_pull_rule()
        res['company_id'] = self.company_id.id
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(StockWarehouse, self).onchange_company_id()
        self.buy_pull_id = False

    @api.multi
    @api.constrains('buy_pull_id', 'company_id')
    def _check_company_buy_pull_id(self):
        for warehouse in self.sudo():
            if warehouse.company_id and warehouse.buy_pull_id.company_id and \
                    warehouse.company_id != warehouse.buy_pull_id.company_id:
                raise ValidationError(
                    _('The Company in the Warehouse and in '
                      ' must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(StockWarehouse, self)._check_company_id()
        for rec in self:
            report = self.env['purchase.report'].search(
                [('picking_type_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      ' is assigned to Report '
                      '%s.' % report.name))
