# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _default_sale_journal(self):
        super()._default_sale_journal()
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        journal = self.env.ref('point_of_sale.pos_sale_journal',
                               raise_if_not_found=False)
        if journal and journal.sudo().company_id.id == company_id:
            return journal
        return self._default_invoice_journal()

    def _default_invoice_journal(self):
        super()._default_invoice_journal()
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        return self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', company_id)], limit=1)

    def _get_default_location(self):
        super()._get_default_location()
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        return self.env['stock.warehouse'].search(
            [('company_id', '=', company_id)], limit=1).lot_stock_id

    def _default_pricelist(self):
        super()._default_pricelist()
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        company = self.env['res.company'].browse(company_id)
        return self.env['product.pricelist'].search(
            [('currency_id', '=', company.currency_id.id),
             '|', ('company_id', '=', company.id),
             ('company_id', '=', False)], limit=1)

    pricelist_id = fields.Many2one(
        default=_default_pricelist
    )
    journal_id = fields.Many2one(
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
        default=_default_sale_journal,
    )
    journal_ids = fields.Many2many(
        domain="[('journal_user', '=', True ), "
               "('type', 'in', ['bank', 'cash']), "
               "('company_id', '=', company_id)]",
    )
    invoice_journal_id = fields.Many2one(
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
        default=_default_invoice_journal,
    )
    stock_location_id = fields.Many2one(
        domain="[('usage', '=', 'internal'),"
               "'|',('company_id','=',False),('company_id','=',company_id)]",
        default=_get_default_location
    )

    @api.model
    def create(self, vals):
        # If we are creating the pos.config with a specific company, and
        # we are not indicating an invoice journal or location, we
        # propose a default that is consistent with the company provided.
        company_id = vals.get('company_id', False)
        invoice_journal_id = vals.get('invoice_journal_id', False)
        stock_location_id = vals.get('stock_location_id', False)

        if company_id and not invoice_journal_id:
            invoice_journal = self.with_context(
                company_id=company_id)._default_invoice_journal()
            vals['invoice_journal_id'] = invoice_journal.id
        if company_id and not stock_location_id:
            stock_location = self.with_context(
                company_id=company_id)._get_default_location()
            vals['stock_location_id'] = stock_location.id
        return super(PosConfig, self).create(vals)

    @api.multi
    def write(self, vals):
        for pos_config in self:
            if vals.get('company_id') and not vals.get('sequence_id', False):
                sequence_id = vals.get('sequence_id',
                                       pos_config.sequence_id.id)
                sequence = self.env[
                    'ir.sequence'].browse(sequence_id)
                if sequence and sequence.company_id.id != vals['company_id']:
                    sequence.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
            if vals.get('company_id') and not vals.get(
                    'sequence_line_id', False):
                sequence_id = vals.get('sequence_line_id',
                                       pos_config.sequence_line_id.id)
                sequence = self.env[
                    'ir.sequence'].browse(sequence_id)
                if sequence and sequence.company_id.id != vals['company_id']:
                    sequence.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
        return super(PosConfig, self).write(vals)

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
        if not self.journal_id or not self.journal_id.check_company(
                self.company_id):
            self.journal_id = self.with_context(
                company_id=self.company_id.id)._default_sale_journal()
        if not self.invoice_journal_id or not \
                self.invoice_journal_id.check_company(self.company_id):
            self.invoice_journal_id = self.with_context(
                company_id=self.company_id.id)._default_invoice_journal()
        if not self.tip_product_id.check_company(self.company_id):
            self.tip_product_id = False
        if not self.pricelist_id or not self.pricelist_id.check_company(
                self.company_id):
            self.pricelist_id = self.with_context(
                company_id=self.company_id.id)._default_pricelist()
        if not self.stock_location_id or not \
                self.stock_location_id.check_company(self.company_id):
            self.stock_location_id = self.with_context(
                company_id=self.company_id.id)._get_default_location()
        if not self.default_fiscal_position_id.check_company(self.company_id):
            self.default_fiscal_position_id = False

    @api.multi
    @api.constrains('company_id', 'invoice_journal_id')
    def _check_company_id_invoice_journal_id(self):
        for rec in self.sudo():
            if not rec.invoice_journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Invoice Journal must be the same.'))

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
