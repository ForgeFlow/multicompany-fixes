from odoo import fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    company_id = fields.Many2one(
        'res.company', related='picking_id.company_id', string='Company',
        readonly=True, default=lambda self: self.env.user.company_id)
