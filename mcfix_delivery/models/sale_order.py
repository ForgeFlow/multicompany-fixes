from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        if not self.carrier_id.check_company(self.company_id):
            self.with_context(force_company=self.company_id.id
                              ).onchange_partner_id_carrier_id()

    @api.onchange('partner_id')
    def onchange_partner_id_carrier_id(self):
        super(SaleOrder,
              self.with_context(force_company=self.company_id.id
                                )).onchange_partner_id_carrier_id()

    @api.multi
    @api.constrains('company_id', 'carrier_id')
    def _check_company_id_carrier_id(self):
        for rec in self.sudo():
            if not rec.carrier_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Sale Order and in '
                      'Delivery Carrier must be the same.'))
