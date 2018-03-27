from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(PurchaseOrder, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        super(PurchaseOrder, self)._onchange_picking_type_id()
        if self.picking_type_id:
            self.company_id = self.picking_type_id.warehouse_id.company_id.id

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self.with_context(
            force_company=self.company_id.id)).onchange_partner_id()
        if self.partner_id:
            self.currency_id = (
                self.partner_id.property_purchase_currency_id.id or
                self.company_id.currency_id.id
            )
        return res

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        res['context']['default_company_id'] = self.company_id.id
        return res

    def set_picking_type(self):
        self.picking_type_id = self.with_context(
            company_id=self.company_id.id
        )._default_picking_type()

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.picking_type_id.warehouse_id.\
                company_id and self.picking_type_id.warehouse_id.\
                company_id != self.company_id:
            self.set_picking_type()
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = False
        if self.company_id and self.dest_address_id.company_id and \
                self.dest_address_id.company_id != self.company_id:
            self.dest_address_id = False
        self.with_context(force_company=self.company_id.id)._compute_tax_id()

    @api.multi
    @api.constrains('company_id', 'invoice_ids')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Purchase Order and in '
                          'Account Invoice (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'picking_ids')
    def _check_company_id_picking_ids(self):
        for rec in self.sudo():
            for line in rec.picking_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Purchase Order and in '
                          'Stock Picking (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'payment_term_id')
    def _check_company_id_payment_term_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.payment_term_id.company_id and\
                    rec.company_id != rec.payment_term_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Account Payment Term must be the same.'))

    @api.multi
    @api.constrains('company_id', 'dest_address_id')
    def _check_company_id_dest_address_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.dest_address_id.company_id and\
                    rec.company_id != rec.dest_address_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.fiscal_position_id.company_id and\
                    rec.company_id != rec.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Account Fiscal Position must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('purchase_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Purchase Order is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['purchase.order.line'].search(
                    [('order_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Purchase Order is assigned to Purchase Order Line '
                          '(%s).' % field.name_get()[0][1]))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.constrains('company_id', 'taxes_id')
    def _check_company_id_taxes_id(self):
        for rec in self.sudo():
            for line in rec.taxes_id:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Purchase Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'orderpoint_id')
    def _check_company_id_orderpoint_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.orderpoint_id.company_id and\
                    rec.company_id != rec.orderpoint_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Stock Warehouse Orderpoint must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_analytic_id.company_id and\
                    rec.company_id != rec.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'order_id')
    def _check_company_id_order_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.order_id.company_id and\
                    rec.company_id != rec.order_id.company_id:
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Purchase Order must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.move'].search(
                    [('created_purchase_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Purchase Order Line is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('purchase_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Purchase Order Line is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.line'].search(
                    [('purchase_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Purchase Order Line is assigned to '
                          'Account Invoice Line (%s)'
                          '.' % field.name_get()[0][1]))

    def _suggest_quantity(self):
        self.taxes_id = self.taxes_id.filtered(
            lambda r: r.company_id == self.order_id.company_id)
        return super()._suggest_quantity()
