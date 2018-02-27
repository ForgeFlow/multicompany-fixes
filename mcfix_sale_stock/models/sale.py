from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        if self.company_id and self.warehouse_id.company_id \
                and self.warehouse_id.company_id != self.company_id:
            self.warehouse_id = False

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.warehouse_id.company_id and\
                    rec.company_id != rec.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Stock Warehouse must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(SaleOrder, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.picking'].search(
                    [('sale_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Sale Order is assigned to Stock Picking '
                          '(%s).' % field.name_get()[0][1]))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.constrains('company_id', 'route_id')
    def _check_company_id_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.route_id.company_id and\
                    rec.company_id != rec.route_id.company_id:
                raise ValidationError(
                    _('The Company in the Sale Order Line and in '
                      'Stock Location Route must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(SaleOrderLine, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.move'].search(
                    [('sale_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Sale Order Line is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
