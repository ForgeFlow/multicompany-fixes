from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        if 'company_id' in rec and rec['company_id']:
            warehouse_ids = self.env['stock.warehouse'].search(
                [('company_id', '=', rec['company_id'])], limit=1)
            if warehouse_ids:
                rec.update({
                    'warehouse_id': warehouse_ids[0].id})
        return rec

    @api.onchange('team_id')
    def onchange_team_id_change_warehouse(self):
        super(SaleOrder, self).onchange_team_id()
        if self.team_id and self.team_id.company_id:
            warehouses = self.env['stock.warehouse'].search(
                [('company_id', '=', self.team_id.company_id.id)], limit=1)
            if warehouses:
                self.warehouse_id = warehouses[0]

    @api.onchange('company_id')
    def onchange_company_id(self):
        res = super(SaleOrder, self).onchange_company_id()
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1)
        if warehouses:
            self.warehouse_id = warehouses[0]
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            self.company_id = self.warehouse_id.company_id

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_warehouse_company(self):
        for rec in self.sudo():
            if (rec.warehouse_id and rec.warehouse_id.company_id and
                    rec.warehouse_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the warehouse '
                                        'must match with that of the '
                                        'quote/sales order'))

    @api.constrains('partner_id', 'company_id')
    def _check_partner_company(self):
        for rec in self.sudo():
            if (rec.partner_id.company_id and
                    rec.partner_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the partner '
                                        'must match with that of the '
                                        'quote/sales order'))
