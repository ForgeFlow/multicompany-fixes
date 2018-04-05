from odoo import api, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('sale.order', [('carrier_id', '=', self.id)]),
            ('stock.picking', [('carrier_id', '=', self.id)]),
        ]
        return res
