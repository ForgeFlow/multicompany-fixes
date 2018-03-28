from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(StockMove, self)._onchange_company_id()
        if not self.origin_returned_move_id:
            if not self.created_purchase_line_id.check_company(
                self.company_id
            ):
                self.created_purchase_line_id = False
            if not self.purchase_line_id.check_company(self.company_id):
                self.purchase_line_id = False

    @api.multi
    @api.constrains('company_id', 'created_purchase_line_id')
    def _check_company_id_created_purchase_line_id(self):
        for rec in self.sudo():
            if not rec.created_purchase_line_id.company_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Purchase Order Line must be the same.'))

    @api.multi
    @api.constrains('company_id', 'purchase_line_id')
    def _check_company_id_purchase_line_id(self):
        for rec in self.sudo():
            if not rec.purchase_line_id.company_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Purchase Order Line must be the same.'))
