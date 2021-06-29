from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    crm_team_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(PosConfig, self)._onchange_company_id()
        if not self.crm_team_id.check_company(self.company_id):
            self.crm_team_id = self.current_session_id.crm_team_id
