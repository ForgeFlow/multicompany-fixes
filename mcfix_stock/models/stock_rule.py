from odoo import api, fields, models


class ProcurementRule(models.Model):
    _inherit = 'stock.rule'

    route_id = fields.Many2one(check_company=True)
    propagate_warehouse_id = fields.Many2one(check_company=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.location_src_id.check_company(self.company_id):
            self.location_src_id = False
        if not self.location_id.check_company(self.company_id):
            self.location_id = self.location_src_id
        if not self.route_id.check_company(self.company_id):
            self.route_id.company_id = self.company_id
        # if not self.partner_address_id.check_company(self.company_id):
        #     self.partner_address_id = False
        if not self.warehouse_id.check_company(self.company_id):
            self.warehouse_id = self.picking_type_id.warehouse_id
        if not self.propagate_warehouse_id.check_company(self.company_id):
            self.propagate_warehouse_id = False

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.move', [('rule_id', '=', self.id)]),
            ('stock.warehouse', [('mto_pull_id', '=', self.id)]),
        ]
        return res
