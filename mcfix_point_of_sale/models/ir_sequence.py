# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("pos.config", [("sequence_id", "=", self.id)]),
            ("pos.config", [("sequence_line_id", "=", self.id)]),
        ]
        return res
