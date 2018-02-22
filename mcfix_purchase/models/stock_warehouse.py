from odoo import api, models, _
from odoo.exceptions import ValidationError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     super(Warehouse, self)._onchange_company_id()
    #     if self.company_id and self.buy_pull_id.company_id and \
    #             self.buy_pull_id.company_id != self.company_id:
    #         self.buy_pull_id = self.default_resupply_wh_id.buy_pull_id

    @api.multi
    @api.constrains('company_id', 'buy_pull_id')
    def _check_company_id_buy_pull_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.buy_pull_id.company_id and\
                    rec.company_id != rec.buy_pull_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Procurement Rule must be the same.'))


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(Orderpoint, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['purchase.order.line'].search(
                    [('orderpoint_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse Orderpoint is assigned to '
                          'Purchase Order Line (%s)'
                          '.' % field.name_get()[0][1]))
