# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockInventory, self).name_get()
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
        self.location_id = False
        self.package_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for inventory in self.sudo():
            if inventory.company_id and inventory.location_id.company_id and \
                    inventory.company_id != inventory.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Inventory and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('package_id', 'company_id')
    def _check_company_package_id(self):
        for inventory in self.sudo():
            if inventory.company_id and inventory.package_id.company_id and \
                    inventory.company_id != inventory.package_id.company_id:
                raise ValidationError(
                    _('The Company in the Inventory and in '
                      'Package must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            inventory_line = self.env['stock.inventory.line'].search(
                [('inventory_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if inventory_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Inventory is assigned to Inventory Line '
                      '%s.' % inventory_line.name))
            move = self.env['stock.move'].search(
                [('inventory_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Inventory is assigned to Move '
                      '%s.' % move.name))


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockInventoryLine, self).name_get()
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
        self.inventory_id = False
        self.location_id = False
        self.package_id = False
        self.inventory_location_id = False

    @api.multi
    @api.constrains('inventory_id', 'company_id')
    def _check_company_inventory_id(self):
        for inventory_line in self.sudo():
            if inventory_line.company_id and inventory_line.inventory_id.\
                    company_id and inventory_line.company_id != inventory_line\
                    .inventory_id.company_id:
                raise ValidationError(
                    _('The Company in the Inventory Line and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for inventory_line in self.sudo():
            if inventory_line.company_id and inventory_line.location_id.\
                    company_id and inventory_line.company_id != inventory_line\
                    .location_id.company_id:
                raise ValidationError(
                    _('The Company in the Inventory Line and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('package_id', 'company_id')
    def _check_company_package_id(self):
        for inventory_line in self.sudo():
            if inventory_line.company_id and inventory_line.package_id.\
                    company_id and inventory_line.company_id != inventory_line\
                    .package_id.company_id:
                raise ValidationError(
                    _('The Company in the Inventory Line and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('inventory_location_id', 'company_id')
    def _check_company_inventory_location_id(self):
        for inventory_line in self.sudo():
            if inventory_line.company_id and inventory_line.\
                    inventory_location_id.company_id and inventory_line.\
                    company_id != inventory_line.inventory_location_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Inventory Line and in '
                      ' must be the same.'))
        return True
