from odoo import api, models


class CrmTeam(models.Model):
    _inherit = "crm.team"
    _check_company_auto = True

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.message_partner_ids,
        ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("res.partner", [("team_id", "=", self.id)]),
        ]
        return res
