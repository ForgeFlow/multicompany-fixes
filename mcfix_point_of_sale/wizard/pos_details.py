# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PosDetails(models.TransientModel):
    _inherit = "pos.details.wizard"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda s: s.env.company_id,
    )
    pos_config_ids = fields.Many2many(
        required=True,
        default=lambda s: s.env["pos.config"].search(
            [("company_id", "=", s.company_id.id)]
        ),
    )

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.company_id:
            self.pos_config_ids = self.env["pos.config"].search(
                [("company_id", "=", self.company_id.id)]
            )
        else:
            self.pos_config_ids = self.env["pos.config"].search([])

    def generate_report(self):
        result = super(PosDetails, self).generate_report()
        result["data"].update({"company_id": self.company_id.id})
        return result
