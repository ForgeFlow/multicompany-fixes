from odoo import api, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(PosConfig, self)._onchange_company_id()
        if not self.crm_team_id.check_company(self.company_id):
            self.crm_team_id = self.current_session_id.crm_team_id

    @api.multi
    @api.constrains('company_id', 'crm_team_id')
    def _check_company_id_crm_team_id(self):
        for rec in self.sudo():
            if not rec.crm_team_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Crm Team must be the same.'))
