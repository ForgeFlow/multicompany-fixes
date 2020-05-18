from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_line_id = fields.Many2one(check_company=True)
    created_purchase_line_id = fields.Many2one(check_company=True)

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
