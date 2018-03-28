from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        if not self.warehouse_id.check_company(self.company_id):
            self.warehouse_id = False

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if not rec.warehouse_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Stock Warehouse must be the same.'))

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.picking_ids, ]
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.constrains('company_id', 'route_id')
    def _check_company_id_route_id(self):
        for rec in self.sudo():
            if not rec.route_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Sale Order Line and in '
                      'Stock Location Route must be the same.'))

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.move_ids, ]
        return res
