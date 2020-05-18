# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"
    _check_company_auto = True

    def _default_company(self):
        return self.env.context.get('company_id') or self.env.company_id.id

    company_id = fields.Many2one(default=_default_company)
    account_move = fields.Many2one(check_company=True)
    picking_id = fields.Many2one(check_company=True)
    pricelist_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    fiscal_position_id = fields.Many2one(check_company=True)
    session_id = fields.Many2one(check_company=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.pricelist_id.check_company(self.company_id):
            self.pricelist_id = self.config_id.pricelist_id

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.lines, self.payment_ids, ]
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    _check_company_auto = True

    tax_ids = fields.Many2many(check_company=True)
