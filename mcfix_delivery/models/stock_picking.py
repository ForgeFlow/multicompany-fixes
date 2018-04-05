from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(StockPicking, self)._onchange_company_id()
        if not self.carrier_id.check_company(self.company_id):
            self.carrier_id = False

    @api.multi
    @api.constrains('company_id', 'carrier_id')
    def _check_company_id_carrier_id(self):
        for rec in self.sudo():
            if not rec.carrier_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'the Carrier must be the same.'))
