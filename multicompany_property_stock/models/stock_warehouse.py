from odoo import fields, models


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    company_id = fields.Many2one(readonly=False)
