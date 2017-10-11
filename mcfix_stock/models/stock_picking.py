# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockPicking, self).name_get()
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
        self.backorder_id = False
        self.location_id = False
        self.location_dest_id = False

    @api.multi
    @api.constrains('backorder_id', 'company_id')
    def _check_company_backorder_id(self):
        for picking in self.sudo():
            if picking.company_id and picking.backorder_id.company_id and \
                    picking.company_id != picking.backorder_id.company_id:
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'Backorder must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for picking in self.sudo():
            if picking.company_id and picking.location_id and \
                    picking.company_id != picking.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('location_dest_id', 'company_id')
    def _check_company_location_dest_id(self):
        for picking in self.sudo():
            if picking.company_id and picking.location_dest_id and \
                    picking.company_id != picking.location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'Location must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            move = self.env['stock.move'].search(
                [('picking_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Picking is assigned to Move '
                      '%s.' % move.name))
            move = self.env['stock.move'].search(
                [('backorder_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Picking is assigned to Move '
                      '%s.' % move.name))
            picking = self.search(
                [('backorder_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if picking:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Picking is assigned to Picking '
                      '%s.' % picking.name))
