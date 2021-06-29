from odoo import models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.pos_config_ids,
        ]
        return res
