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
        if self.picking_type_id and not self.env.context.get(
            'no_change_company'
        ):
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
        if not self.picking_type_id.warehouse_id.check_company(
            self.company_id
        ):
            self.set_picking_type()
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.dest_address_id.check_company(self.company_id):
            self.dest_address_id = False
        self.order_line.change_company_id()

    @api.multi
    @api.constrains('company_id', 'invoice_ids')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Purchase Order and in '
                          'Account Invoice (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'picking_ids')
    def _check_company_id_picking_ids(self):
        for rec in self.sudo():
            for line in rec.picking_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Purchase Order and in '
                          'Stock Picking (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'payment_term_id')
    def _check_company_id_payment_term_id(self):
        for rec in self.sudo():
            if not rec.payment_term_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Account Payment Term must be the same.'))

    @api.multi
    @api.constrains('company_id', 'dest_address_id')
    def _check_company_id_dest_address_id(self):
        for rec in self.sudo():
            if not rec.dest_address_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if not rec.fiscal_position_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Purchase Order and in '
                      'Account Fiscal Position must be the same.'))

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_ids, self.order_line, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.invoice', [('purchase_id', '=', self.id)]),
        ]
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _suggest_quantity(self):
        self.taxes_id = self.taxes_id.filtered(
            lambda r: r.company_id == self.order_id.company_id)
        if not self.account_analytic_id:
            self.account_analytic_id = self.default_account_analytic()
        return super()._suggest_quantity()

    @api.multi
    def change_company_id(self):
        for line in self:
            line._compute_tax_id()
            if not line.account_analytic_id.check_company(line.company_id):
                line.account_analytic_id = line.get_default_account_analytic()

    @api.model
    def default_account_analytic(self):
        return False

    @api.multi
    @api.constrains('company_id', 'taxes_id')
    def _check_company_id_taxes_id(self):
        for rec in self.sudo():
            for line in rec.taxes_id:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Purchase Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'orderpoint_id')
    def _check_company_id_orderpoint_id(self):
        for rec in self.sudo():
            if not rec.orderpoint_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Stock Warehouse Orderpoint must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'order_id')
    def _check_company_id_order_id(self):
        for rec in self.sudo():
            if not rec.order_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Purchase Order Line and in '
                      'Purchase Order must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_lines, self.move_ids, self.move_dest_ids, ]
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.company_id = self.order_id.company_id
        result = super(
            PurchaseOrderLine,
            self.with_context(not_display_company=True)).onchange_product_id()
        self._compute_tax_id()
        return result
