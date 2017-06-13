from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        if rec['company_id']:
            warehouse_ids = self.env['stock.warehouse'].search(
                [('company_id', '=', rec['company_id'])], limit=1)
            if warehouse_ids:
                rec.update({
                    'warehouse_id': warehouse_ids[0].id})
        return rec
