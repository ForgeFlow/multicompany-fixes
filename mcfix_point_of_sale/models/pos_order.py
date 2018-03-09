from odoo import api, models, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.account_move.check_company(self.company_id):
            self.account_move = False
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
            # self.partner_id = self.company_id.partner_id
        if not self.fiscal_position_id.check_company(self.company_id):
            self.fiscal_position_id = self.invoice_id.fiscal_position_id
        if not self.picking_id.check_company(self.company_id):
            self.picking_id = False
        if not self.invoice_id.check_company(self.company_id):
            self.invoice_id = False
        if not self.pricelist_id.check_company(self.company_id):
            self.pricelist_id = self.config_id.pricelist_id

    @api.multi
    @api.constrains('company_id', 'account_move')
    def _check_company_id_account_move(self):
        for rec in self.sudo():
            if not rec.account_move.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if not rec.fiscal_position_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'picking_id')
    def _check_company_id_picking_id(self):
        for rec in self.sudo():
            if not rec.picking_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Stock Picking must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if not rec.invoice_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'pricelist_id')
    def _check_company_id_pricelist_id(self):
        for rec in self.sudo():
            if not rec.pricelist_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Product Pricelist must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.lines, self.statement_ids, ]
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.product_id.check_company(self.company_id):
            self.product_id = False
        # if not self.tax_ids.check_company(self.company_id):
        #     self.tax_ids = self.env['account.tax'].search(
        #             [('____id', '=', self.id),
        #              ('company_id', '=', False),
        #              ('company_id', '=', self.company_id.id)])
        if not self.order_id.check_company(self.company_id):
            self.order_id = False
        # if not self.tax_ids_after_fiscal_position.check_company(
        #     self.company_id
        # ):
        #     self.tax_ids_after_fiscal_position = self.env['account.tax'].\
        #         search(
        #             [('____id', '=', self.id),
        #              ('company_id', '=', False),
        #              ('company_id', '=', self.company_id.id)])

    # @api.multi
    # @api.constrains('company_id', 'product_id')
    # def _check_company_id_product_id(self):
    #     for rec in self.sudo():
    #         if not rec.product_id.check_company(rec.company_id):
    #             raise ValidationError(
    #                 _('The Company in the Pos Order Line and in '
    #                   'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_ids')
    def _check_company_id_tax_ids(self):
        for rec in self.sudo():
            for line in rec.tax_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Pos Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'order_id')
    def _check_company_id_order_id(self):
        for rec in self.sudo():
            if not rec.order_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Order Line and in '
                      'Pos Order must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_ids_after_fiscal_position')
    def _check_company_id_tax_ids_after_fiscal_position(self):
        for rec in self.sudo():
            for line in rec.tax_ids_after_fiscal_position:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Pos Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])
