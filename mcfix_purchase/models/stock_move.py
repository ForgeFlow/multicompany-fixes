from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(StockMove, self)._onchange_company_id()
        if not self.origin_returned_move_id:
            if self.company_id and self.created_purchase_line_id.company_id \
                    and self.created_purchase_line_id.company_id != self.\
                    company_id:
                self.created_purchase_line_id = False
            if self.company_id and self.purchase_line_id.company_id and \
                    self.purchase_line_id.company_id != self.company_id:
                self.purchase_line_id = False

    @api.multi
    @api.constrains('company_id', 'created_purchase_line_id')
    def _check_company_id_created_purchase_line_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.created_purchase_line_id.company_id and\
                    rec.company_id != rec.created_purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Purchase Order Line must be the same.'))

    @api.multi
    @api.constrains('company_id', 'purchase_line_id')
    def _check_company_id_purchase_line_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.purchase_line_id.company_id and\
                    rec.company_id != rec.purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Purchase Order Line must be the same.'))
