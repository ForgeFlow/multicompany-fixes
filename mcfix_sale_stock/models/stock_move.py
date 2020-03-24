from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.constrains('company_id', 'sale_line_id')
    def _check_company_id_sale_line_id(self):
        for rec in self.sudo():
            if not rec.sale_line_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Sale Order Line must be the same.'))
