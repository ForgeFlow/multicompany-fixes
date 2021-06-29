# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"
    _check_company_auto = True
