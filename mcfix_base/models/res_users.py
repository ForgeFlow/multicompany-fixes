# Copyright 2019 Creu Blanca
# Copyright 2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals):
        # We reset the company of the partner to blank
        users = super(Users, self).create(vals)
        for user in users:
            if user.partner_id.company_id:
                user.partner_id.write({'company_id': False})
        return users

    def write(self, values):
        # We reset the company of the partner to blank
        res = super(Users, self).write(values)
        if 'company_id' in values:
            for user in self:
                # if partner is global we keep it that way
                if user.partner_id.company_id:
                    user.partner_id.write({'company_id': False})
        return res
