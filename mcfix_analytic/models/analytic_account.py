# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _check_company_auto = True

    group_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)

    @api.depends('company_id')
    def name_get(self):
        names = super(AccountAnalyticAccount, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _check_company_auto = True

    account_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    tag_ids = fields.Many2many(check_company=True)
