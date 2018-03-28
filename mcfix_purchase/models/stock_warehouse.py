from odoo import api, models, _
from odoo.exceptions import ValidationError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     super(Warehouse, self)._onchange_company_id()
    #     if not self.buy_pull_id.check_company(self.company_id):
    #         self.buy_pull_id = self.default_resupply_wh_id.buy_pull_id

    @api.multi
    @api.constrains('company_id', 'buy_pull_id')
    def _check_company_id_buy_pull_id(self):
        for rec in self.sudo():
            if not rec.buy_pull_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Procurement Rule must be the same.'))


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order.line', [('orderpoint_id', '=', self.id)]),
        ]
        return res
