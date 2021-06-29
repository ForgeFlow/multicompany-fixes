from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    stock_move_id = fields.Many2one(check_company=True)
