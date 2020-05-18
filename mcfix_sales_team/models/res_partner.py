from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    team_id = fields.Many2one(check_compnay=True)
