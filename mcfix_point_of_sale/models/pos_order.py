# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PosOrder, self).name_get()
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
        self.pricelist_id = False
        self.config_id = False
        self.invoice_id = False
        self.account_move = False
        self.picking_id = False
        self.location_id = False
        self.sale_journal = False
        self.fiscal_position_id = False

    @api.multi
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for order in self.sudo():
            if order.company_id and order.pricelist_id.company_id and \
                    order.company_id != order.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Pricelist must be the same.'))
        return True

    @api.multi
    @api.constrains('config_id', 'company_id')
    def _check_company_config_id(self):
        for order in self.sudo():
            if order.company_id and order.config_id.company_id and \
                    order.company_id != order.config_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Pos Config must be the same.'))
        return True

    @api.multi
    @api.constrains('invoice_id', 'company_id')
    def _check_company_invoice_id(self):
        for order in self.sudo():
            if order.company_id and order.invoice_id.company_id and \
                    order.company_id != order.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Invoice must be the same.'))
        return True

    @api.multi
    @api.constrains('account_move', 'company_id')
    def _check_company_account_move(self):
        for order in self.sudo():
            if order.company_id and order.account_move.company_id and \
                    order.company_id != order.account_move.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Journal Entry must be the same.'))
        return True

    @api.multi
    @api.constrains('picking_id', 'company_id')
    def _check_company_picking_id(self):
        for order in self.sudo():
            if order.company_id and order.picking_id.company_id and \
                    order.company_id != order.picking_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Picking must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for order in self.sudo():
            if order.company_id and order.location_id.company_id and \
                    order.company_id != order.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('sale_journal', 'company_id')
    def _check_company_sale_journal(self):
        for order in self.sudo():
            if order.company_id and order.sale_journal.company_id and \
                    order.company_id != order.sale_journal.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Sale Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position_id(self):
        for order in self.sudo():
            if order.company_id and order.fiscal_position_id.company_id and \
                    order.company_id != order.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Fiscal Position must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            order_line = self.env['pos.order.line'].search(
                [('order_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pos Order is assigned to Pos Order Line '
                      '%s of Pos Order %s.' % (
                          order_line.name, order_line.order_id.name)))
            bank_statement_line = self.env[
                'account.bank.statement.line'].search(
                [('pos_statement_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if bank_statement_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'POS statement is assigned to Bank Statement Line '
                      '%s of Bank Statement %s.' % (
                          bank_statement_line.name,
                          bank_statement_line.statement_id.name)))
            pos_order = self.env['report.pos.order'].search(
                [('order_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pos Order is assigned to Report Pos Order '
                      '%s.' % pos_order.name))


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PosOrderLine, self).name_get()
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
        self.order_id = False
        self.tax_ids = False
        self.tax_ids_after_fiscal_position = False

    @api.multi
    @api.constrains('order_id', 'company_id')
    def _check_company_order_id(self):
        for order_line in self.sudo():
            if order_line.company_id and order_line.order_id.company_id and \
                    order_line.company_id != order_line.order_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Order Line and in '
                      'Pos Order must be the same.'))
        return True

    # point_of_sale / tests / test_point_of_sale_flow.py fails
    # if this is enabled:

    # @api.multi
    # @api.constrains('tax_ids', 'company_id')
    # def _check_company_tax_ids(self):
    #     for order_line in self.sudo():
    #         for account_tax in order_line.tax_ids:
    #             if order_line.company_id and account_tax.company_id and \
    #                     order_line.company_id != account_tax.company_id:
    #                 raise ValidationError(
    #                     _('The Company in the Pos Order Line and in '
    #                       'Tax must be the same.'))
    #     return True

    # @api.multi
    # @api.constrains('tax_ids_after_fiscal_position', 'company_id')
    # def _check_company_tax_ids_after_fiscal_position(self):
    #     for order_line in self.sudo():
    #         for account_tax in order_line.tax_ids_after_fiscal_position:
    #             if order_line.company_id and account_tax.company_id and \
    #                     order_line.company_id != account_tax.company_id:
    #                 raise ValidationError(
    #                     _('The Company in the Pos Order Line and in '
    #                       'Tax must be the same.'))
    #     return True
