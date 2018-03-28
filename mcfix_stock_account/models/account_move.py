from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    @api.constrains('company_id', 'stock_move_id')
    def _check_company_id_stock_move_id(self):
        for rec in self.sudo():
            if not rec.stock_move_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Move and in '
                      'Stock Move must be the same.'))
