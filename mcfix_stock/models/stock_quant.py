# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockQuant, self).name_get()
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
        self.reservation_id = False
        self.history_ids = False
        self.propagated_from_id = False
        self.negative_move_id = False
        self.negative_dest_location_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.location_id.company_id and \
                    quant.company_id != quant.location_id.company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('package_id', 'company_id')
    def _check_company_package_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.package_id.company_id and \
                    quant.company_id != quant.package_id.company_id:
                raise ValidationError(
                    _('The Company in the Quant and in '
                      'Package must be the same.'))
        return True

    @api.multi
    @api.constrains('reservation_id', 'company_id')
    def _check_company_reservation_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.reservation_id.company_id and \
                    quant.company_id != quant.reservation_id.company_id:
                raise ValidationError(
                    _('The Company in the Quant and in '
                      'Reservation must be the same.'))
        return True

    @api.multi
    @api.constrains('history_ids', 'company_id')
    def _check_company_history_ids(self):
        for quant in self.sudo():
            for stock_move in quant.history_ids:
                if quant.company_id and stock_move.company_id and \
                        quant.company_id != stock_move.company_id:
                    raise ValidationError(
                        _('The Company in the Quant and in '
                          'Move must be the same.'))
        return True

    @api.multi
    @api.constrains('propagated_from_id', 'company_id')
    def _check_company_propagated_from_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.propagated_from_id.company_id and \
                    quant.company_id != quant.propagated_from_id.company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Linked Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('negative_move_id', 'company_id')
    def _check_company_negative_move_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.negative_move_id.company_id and \
                    quant.company_id != quant.negative_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Quant and in '
                      'Negative Move must be the same.'))
        return True

    @api.multi
    @api.constrains('negative_dest_location_id', 'company_id')
    def _check_company_negative_dest_location_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.negative_dest_location_id.company_id\
                    and quant.company_id != quant.negative_dest_location_id.\
                    company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Negative Destination Location must '
                                        'be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            quant = self.search(
                [('propagated_from_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Linked Quant is assigned to Quant '
                      '%s.' % quant.name))
            move = self.env['stock.move'].search(
                [('quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant is assigned to Move '
                      '%s.' % move.name))
            move = self.env['stock.move'].search(
                [('reserved_quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Reserved Quant is assigned to Move '
                      '%s.' % move.name))
            quant_package = self.env['stock.quant.package'].search(
                [('quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant_package:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant is assigned to Quant Package '
                      '%s.' % quant_package.name))
            quant_package = self.env['stock.quant.package'].search(
                [('children_quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant_package:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant is assigned to Quant Package '
                      '%s.' % quant_package.name))


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockQuantPackage, self).name_get()
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
        self.quant_ids = False
        self.parent_id = False
        self.ancestor_ids = False
        self.children_quant_ids = False
        self.children_ids = False
        self.location_id = False

    @api.multi
    @api.constrains('quant_ids', 'company_id')
    def _check_company_quant_ids(self):
        for quant_package in self.sudo():
            for stock_quant in quant_package.quant_ids:
                if quant_package.company_id and stock_quant.company_id and \
                        quant_package.company_id != stock_quant.company_id:
                    raise ValidationError(
                        _('The Company in the Quant Package and in '
                          'Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('parent_id', 'company_id')
    def _check_company_parent_id(self):
        for quant_package in self.sudo():
            if quant_package.company_id and quant_package.parent_id.company_id\
                    and quant_package.company_id != quant_package.parent_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Quant Package and in '
                      'Parent Package must be the same.'))
        return True

    @api.multi
    @api.constrains('ancestor_ids', 'company_id')
    def _check_company_ancestor_ids(self):
        for quant_package in self.sudo():
            for stock_quant_package in quant_package.ancestor_ids:
                if quant_package.company_id and stock_quant_package.company_id\
                        and quant_package.company_id != stock_quant_package.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Quant Package and in '
                          'Ancestor Package must be the same.'))
        return True

    @api.multi
    @api.constrains('children_quant_ids', 'company_id')
    def _check_company_children_quant_ids(self):
        for quant_package in self.sudo():
            for stock_quant in quant_package.children_quant_ids:
                if quant_package.company_id and stock_quant.company_id and \
                        quant_package.company_id != stock_quant.company_id:
                    raise ValidationError(
                        _('The Company in the Quant Package and in '
                          'Child Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('children_ids', 'company_id')
    def _check_company_children_ids(self):
        for quant_package in self.sudo():
            for stock_quant_package in quant_package.children_ids:
                if quant_package.company_id and stock_quant_package.company_id\
                        and quant_package.company_id != stock_quant_package.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Quant Package and in '
                          'Child Package must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for quant_package in self.sudo():
            if quant_package.company_id and quant_package.location_id.\
                    company_id and quant_package.company_id != quant_package.\
                    location_id.company_id:
                raise ValidationError(
                    _('The Company in the Quant Package and in '
                      'Location must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            inventory_line = self.env['stock.inventory.line'].search(
                [('package_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if inventory_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant Package is assigned to Inventory Line '
                      '%s in Inventory %s.' % (
                       inventory_line.name, inventory_line.inventory_id.name)))
            quant = self.env['stock.quant'].search(
                [('package_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant Package is assigned to Quant '
                      '%s.' % quant.name))
            quant_package = self.search(
                [('parent_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant_package:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant Package is assigned to Quant Package '
                      '%s.' % quant_package.name))
            quant_package = self.search(
                [('ancestor_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant_package:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Ancestor Package is assigned to Quant Package '
                      '%s.' % quant_package.name))
            quant_package = self.search(
                [('children_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant_package:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant Package is assigned to Quant Package '
                      '%s.' % quant_package.name))
            inventory = self.env['stock.inventory'].search(
                [('package_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if inventory:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Quant Package is assigned to Inventory '
                      '%s.' % inventory.name))
