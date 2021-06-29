# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    _check_company_auto = True

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
