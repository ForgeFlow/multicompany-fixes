from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_line_id = fields.Many2one(check_company=True)
