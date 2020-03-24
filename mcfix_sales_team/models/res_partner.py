from odoo import api, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     super(Partner, self)._onchange_company_id()
    #     if not self.team_id.check_company(self.company_id):
    #         self.team_id = False

    @api.multi
    @api.constrains('company_id', 'team_id')
    def _check_company_id_team_id(self):
        for rec in self.sudo():
            if not rec.team_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Res Partner and in '
                      'Crm Team must be the same.'))
