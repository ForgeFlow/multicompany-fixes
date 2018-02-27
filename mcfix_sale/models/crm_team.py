from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(CrmTeam, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('team_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Crm Team is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['sale.order'].search(
                    [('team_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Crm Team is assigned to Sale Order '
                          '(%s).' % field.name_get()[0][1]))
