from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        # This method can be removed when
        # https://github.com/odoo/odoo/pull/24063 is merged.
        super(SaleOrder, self)._default_warehouse_id()
        company = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        if not self.warehouse_id.check_company(self.company_id):
            self.set_warehouse()

    def set_warehouse(self):
        self.warehouse_id = self.with_context(
            company_id=self.company_id.id
        )._default_warehouse_id()

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if not rec.warehouse_id.check_company(rec):
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
            if not rec.route_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Sale Order Line and in '
                      'Stock Location Route must be the same.'))

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.move_ids, ]
        return res
