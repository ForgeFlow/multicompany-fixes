from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.analytic_account_id.company_id and \
                self.analytic_account_id.company_id != self.company_id:
            self.analytic_account_id = False
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = False
        if self.company_id and self.team_id.company_id and \
                self.team_id.company_id != self.company_id:
            self.team_id = False
        if self.company_id and self.partner_invoice_id.company_id and \
                self.partner_invoice_id.company_id != self.company_id:
            self.partner_invoice_id = False
        if self.company_id and self.partner_shipping_id.company_id and \
                self.partner_shipping_id.company_id != self.company_id:
            self.partner_shipping_id = False
        if self.company_id and self.fiscal_position_id.company_id and \
                self.fiscal_position_id.company_id != self.company_id:
            self.fiscal_position_id = False
        if self.company_id and self.pricelist_id.company_id and \
                self.pricelist_id.company_id != self.company_id:
            self.pricelist_id = False
        if self.company_id and self.payment_term_id.company_id and \
                self.payment_term_id.company_id != self.company_id:
            self.payment_term_id = False
        self.with_context(force_company=self.company_id.id)._compute_tax_id()

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        company_id = self.company_id.id or self.env.user.company_id.id
        super(SaleOrder, self.with_context(force_company=company_id)).\
            onchange_partner_id()

    @api.multi
    def _prepare_invoice(self):
        company_id = self.company_id.id or self.env.user.company_id.id
        return super(SaleOrder, self.with_context(
            company_id=company_id,
            force_company=company_id))._prepare_invoice()

    @api.multi
    @api.constrains('company_id', 'team_id')
    def _check_company_id_team_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.team_id.company_id and\
                    rec.company_id != rec.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Crm Team must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_invoice_id')
    def _check_company_id_partner_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_invoice_id.company_id and\
                    rec.company_id != rec.partner_invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_shipping_id')
    def _check_company_id_partner_shipping_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_shipping_id.company_id and\
                    rec.company_id != rec.partner_shipping_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.fiscal_position_id.company_id and\
                    rec.company_id != rec.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'pricelist_id')
    def _check_company_id_pricelist_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.pricelist_id.company_id and\
                    rec.company_id != rec.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Product Pricelist must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'analytic_account_id')
    def _check_company_id_analytic_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.analytic_account_id.company_id and\
                    rec.company_id != rec.analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id')
    def _check_company_id_invoice_ids(self):
        for rec in self.sudo():
            for line in rec.invoice_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Sale Order and in '
                          'Account Invoice (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'payment_term_id')
    def _check_company_id_payment_term_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.payment_term_id.company_id and\
                    rec.company_id != rec.payment_term_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Account Payment Term must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['sale.order.line'].search(
                    [('order_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Sale Order is assigned to Sale Order Line '
                          '(%s).' % field.name_get()[0][1]))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(SaleOrderLine, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        company_id = self.company_id.id or self.env.user.company_id.id
        return super(SaleOrderLine,
                     self.with_context(force_company=company_id)).\
            _prepare_invoice_line(qty=qty)

    @api.multi
    @api.constrains('company_id', 'invoice_lines')
    def _check_company_id_invoice_lines(self):
        for rec in self.sudo():
            for line in rec.invoice_lines:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Sale Order Line and in '
                          'Account Invoice Line (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_id')
    def _check_company_id_tax_id(self):
        for rec in self.sudo():
            for line in rec.tax_id:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Sale Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'order_id')
    def _check_company_id_order_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.order_id.company_id and\
                    rec.company_id != rec.order_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order Line and in '
                      'Sale Order must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.analytic.line'].search(
                    [('so_line', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Sale Order Line is assigned to '
                          'Account Analytic Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.invoice.line'].search(
                    [('sale_line_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Sale Order Line is assigned to '
                          'Account Invoice Line (%s)'
                          '.' % field.name_get()[0][1]))
