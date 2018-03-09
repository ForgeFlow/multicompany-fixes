from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    journal_id = fields.Many2one(
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
    )
    journal_ids = fields.Many2many(
        domain="[('journal_user', '=', True ), "
               "('type', 'in', ['bank', 'cash']), "
               "('company_id', '=', company_id)]",
    )
    invoice_journal_id = fields.Many2one(
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
    )
    stock_location_id = fields.Many2one(
        domain="[('usage', '=', 'internal'),"
               "'|',('company_id','=',False),('company_id','=',company_id)]",
    )

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(PosConfig, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.journal_ids.check_company(self.company_id):
            self.journal_ids = self.env['account.journal'].search(
                [('journal_user', '=', True),
                 ('type', 'in', ['bank', 'cash']),
                 ('company_id', '=', self.company_id.id)])
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = self.env['account.journal'].search([
                ('company_id', '=', self.company_id.id),
                ('type', '=', 'sale')
            ], limit=1)
            self.invoice_journal_id = self.journal_id
        if not self.tip_product_id.check_company(self.company_id):
            self.tip_product_id = False
        if not self.pricelist_id.check_company(self.company_id):
            self.pricelist_id = self.tip_product_id.pricelist_id
        if not self.stock_location_id.check_company(self.company_id):
            self.stock_location_id = self.env['stock.warehouse'].search(
                [('company_id', '=', self.company_id.id)], limit=1
            ).lot_stock_id
        if not self.default_fiscal_position_id.check_company(self.company_id):
            self.default_fiscal_position_id = False
        # if not self.sequence_id.check_company(self.company_id):
        #     self.sequence_id = False
        # if not self.sequence_line_id.check_company(self.company_id):
        #     self.sequence_line_id = False
        # if not self.available_pricelist_ids.check_company(self.company_id):
        #     self.available_pricelist_ids = self.env['product.pricelist'].\
        #         search(
        #             [('____id', '=', self.id),
        #              ('company_id', '=', False),
        #              ('company_id', '=', self.company_id.id)])
        # if not self.journal_ids.check_company(self.company_id):
        #     self.journal_ids = self.env['account.journal'].search(
        #             [('____id', '=', self.id),
        #              ('company_id', '=', False),
        #              ('company_id', '=', self.company_id.id)])
        # if not self.fiscal_position_ids.check_company(self.company_id):
        #     self.fiscal_position_ids = self.env['account.fiscal.position'].\
        #         search(
        #             [('____id', '=', self.id),
        #              ('company_id', '=', False),
        #              ('company_id', '=', self.company_id.id)])

    @api.multi
    @api.constrains('company_id', 'invoice_journal_id')
    def _check_company_id_invoice_journal_id(self):
        for rec in self.sudo():
            if not rec.invoice_journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'pricelist_id')
    def _check_company_id_pricelist_id(self):
        for rec in self.sudo():
            if not rec.pricelist_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Product Pricelist must be the same.'))

    @api.multi
    @api.constrains('company_id', 'sequence_line_id')
    def _check_company_id_sequence_line_id(self):
        for rec in self.sudo():
            if not rec.sequence_line_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Ir Sequence must be the same.'))

    @api.multi
    @api.constrains('company_id', 'stock_location_id')
    def _check_company_id_stock_location_id(self):
        for rec in self.sudo():
            if not rec.stock_location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'default_fiscal_position_id')
    def _check_company_id_default_fiscal_position_id(self):
        for rec in self.sudo():
            if not rec.default_fiscal_position_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tip_product_id')
    def _check_company_id_tip_product_id(self):
        for rec in self.sudo():
            if not rec.tip_product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'available_pricelist_ids')
    def _check_company_id_available_pricelist_ids(self):
        for rec in self.sudo():
            for line in rec.available_pricelist_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Pos Config and in '
                          'Product Pricelist (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'journal_ids')
    def _check_company_id_journal_ids(self):
        for rec in self.sudo():
            for line in rec.journal_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Pos Config and in '
                          'Account Journal (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'fiscal_position_ids')
    def _check_company_id_fiscal_position_ids(self):
        for rec in self.sudo():
            for line in rec.fiscal_position_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Pos Config and in '
                          'Account Fiscal Position (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'sequence_id')
    def _check_company_id_sequence_id(self):
        for rec in self.sudo():
            if not rec.sequence_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Ir Sequence must be the same.'))
