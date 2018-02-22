from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(ProcurementRule, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.warehouse'].search(
                    [('buy_pull_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Procurement Rule is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
