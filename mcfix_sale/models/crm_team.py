from odoo import models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("account.move", [("team_id", "=", self.id)]),
            ("sale.order", [("team_id", "=", self.id)]),
        ]
        return res
