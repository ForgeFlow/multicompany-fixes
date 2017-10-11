# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PurchaseOrder, self).name_get()
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
        self.invoice_ids = False
        self.picking_ids = False
        self.fiscal_position_id = False
        self.payment_term_id = False

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            if self.partner_id.company_id:
                if self.partner_id.company_id != self.company_id:
                    self.partner_id = False
            self.payment_term_id = self.partner_id.\
                with_context(force_company=self.company_id.id).\
                property_supplier_payment_term_id.id
            self.currency_id = self.partner_id.\
                with_context(force_company=self.company_id.id).\
                property_purchase_currency_id.id or self.env.user.company_id.\
                currency_id.id
        for line in self.order_line:
            line.onchange_product_id()
        return res

    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        result['context']['default_company_id'] = self.company_id.id
        return result

    @api.multi
    @api.constrains('partner_id', 'company_id')
    def _check_partner_company(self):
        for rec in self:
            if (rec.partner_id and rec.partner_id.company_id and
                    rec.partner_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the Partner '
                                        'must match with that of the '
                                        'RFQ/Purchase Order.'))

    @api.multi
    @api.constrains('invoice_ids', 'company_id')
    def _check_company_invoice_ids(self):
        for order in self.sudo():
            for account_invoice in order.invoice_ids:
                if order.company_id and account_invoice.company_id and \
                        order.company_id != account_invoice.company_id:
                    raise ValidationError(
                        _('The Company in the RFQ/Purchase Order and in '
                          'Bill must be the same.'))
        return True

    @api.multi
    @api.constrains('picking_ids', 'company_id')
    def _check_company_picking_ids(self):
        for order in self.sudo():
            for stock_picking in order.picking_ids:
                if order.company_id and stock_picking.company_id and \
                        order.company_id != stock_picking.company_id:
                    raise ValidationError(
                        _('The Company in the RFQ/Purchase Order and in '
                          'Reception must be the same.'))
        return True

    @api.multi
    @api.constrains('payment_term_id', 'company_id')
    def _check_company_payment_term_id(self):
        for order in self.sudo():
            if order.company_id and order.payment_term_id.company_id and \
                    order.company_id != order.payment_term_id.company_id:
                raise ValidationError(
                    _('Configuration error\n'
                      'The Company of the Payment Term must match with that '
                      'of the RFQ/Purchase Order.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position_id(self):
        for order in self.sudo():
            if order.company_id and order.fiscal_position_id.company_id and \
                    order.company_id != order.fiscal_position_id.company_id:
                raise ValidationError(
                    _('Configuration error\n'
                      'The Company of the fiscal position must match with that'
                      ' of the RFQ/Purchase Order.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            order_line = self.env['purchase.order.line'].search(
                [('order_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'RFQ/Purchase Order is assigned to Purchase Order Line '
                      '%s of Purchase Order %s.' % (order_line.name,
                                                    order_line.order_id.name)))
            invoice_line = self.env['account.invoice.line'].search(
                [('purchase_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order is assigned to Invoice Line '
                      '%s of Invoice %s.' % (invoice_line.name,
                                             invoice_line.invoice_id.name)))
            invoice = self.env['account.invoice'].search(
                [('purchase_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order is assigned to Invoice '
                      '%s.' % invoice.name))
            picking = self.env['stock.picking'].search(
                [('purchase_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if picking:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order is assigned to Picking '
                      '%s.' % picking.name))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PurchaseOrderLine, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.taxes_id = False
        self.order_id = False
        self.account_analytic_id = False

    @api.onchange('product_id', 'company_id')
    def onchange_product_id(self):
        if not self.company_id:
            self.company_id = self.order_id.company_id
        result = super(PurchaseOrderLine, self).onchange_product_id()

        fpos = self.order_id.fiscal_position_id or self.order_id.\
            with_context(force_company=self.company_id.id).\
            partner_id.property_account_position_id
        taxes = self.product_id.supplier_taxes_id.filtered(
            lambda r: not self.company_id or r.company_id == self.company_id)
        self.taxes_id = fpos.map_tax(
            taxes, self.product_id, self.order_id.partner_id) if \
            fpos else taxes
        self._suggest_quantity()
        self._onchange_quantity()

        return result

    def _suggest_quantity(self):
        current_quantity = self.product_qty
        super(PurchaseOrderLine, self)._suggest_quantity()
        if current_quantity > self.product_qty:
            self.product_qty = current_quantity

    @api.multi
    @api.constrains('order_id', 'company_id')
    def _check_company_order_id(self):
        for order_line in self.sudo():
            if order_line.company_id and order_line.order_id.company_id and \
                    order_line.company_id != order_line.order_id.company_id:
                raise ValidationError(_('The Company in the Purchase Order '
                                        'Line and in the RFQ/Purchase must be '
                                        'the same.'))
        return True

    @api.multi
    @api.constrains('taxes_id', 'company_id')
    def _check_company_taxes_id(self):
        for order_line in self.sudo():
            for account_tax in order_line.taxes_id:
                if order_line.company_id and account_tax.company_id and \
                        order_line.company_id != account_tax.company_id:
                    raise ValidationError(
                        _('Configuration error\n'
                          'The Company of the tax %s must match with that of '
                          'the RFQ/Purchase Order.'
                          ) % order_line.taxes_id.name)
            return True

    @api.multi
    @api.constrains('account_analytic_id', 'company_id')
    def _check_company_account_analytic_id(self):
        for order_line in self.sudo():
            if order_line.company_id and order_line.account_analytic_id.\
                    company_id and order_line.company_id != order_line.\
                    account_analytic_id.company_id:
                raise ValidationError(_('The Company in the Purchase Order '
                                        'Line and in Analytic Account must be '
                                        'the same.'))
        return True

    @api.multi
    @api.constrains('product_id', 'company_id')
    def _check_product_company(self):
        for rec in self.sudo():
            if (rec.product_id and rec.product_id.company_id and
                    rec.product_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the product %s '
                                        'must match with that of the '
                                        'RFQ/Purchase Order.') %
                                      rec.product_id.name)

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            order = self.env['procurement.order'].search(
                [('purchase_line_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order Line is assigned to Procurement Order '
                      '%s.' % order.name))
            invoice_line = self.env['account.invoice.line'].search(
                [('purchase_line_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order Line is assigned to Invoice Line '
                      '%s of Invoice %s.' % (invoice_line.name,
                                             invoice_line.invoice_id.name)))
            move = self.env['stock.move'].search(
                [('purchase_line_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Order Line is assigned to Stock Move '
                      '%s.' % move.name))
