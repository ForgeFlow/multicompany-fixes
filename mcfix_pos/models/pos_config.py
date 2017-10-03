from odoo import models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.journal_ids = None
        self.journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)],
            limit=1
        )
        self.invoice_journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)],
            limit=1
        )
        self.stock_location_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1
        ).lot_stock_id
        self.fiscal_position_ids = None
        self.default_fiscal_position_id = None
