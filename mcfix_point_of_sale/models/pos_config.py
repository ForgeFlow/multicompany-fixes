# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'
    _check_company_auto = True

    def _default_pricelist(self):
        super()._default_pricelist()
        company_id = self.env.context.get('company_id') or \
            self.env.company_id.id
        company = self.env['res.company'].browse(company_id)
        return self.env['product.pricelist'].search(
            [('currency_id', '=', company.currency_id.id),
             ('company_id', 'in', [False, company.id])], limit=1)

    def _default_sale_journal(self):
        super()._default_sale_journal()
        company_id = self.env.context.get('company_id') or \
            self.env.company_id.id
        return self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', company_id),
             ('code', '=', 'POSS')], limit=1)

    def _default_invoice_journal(self):
        super()._default_invoice_journal()
        company_id = self.env.context.get('company_id') or \
            self.env.company_id.id
        return self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', company_id)], limit=1)

    journal_id = fields.Many2one(
        check_company=True, default=_default_sale_journal,
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
    )
    invoice_journal_id = fields.Many2one(
        check_company=True, default=_default_invoice_journal,
        domain="[('type', '=', 'sale'), ('company_id', '=', company_id)]",
    )
    picking_type_id = fields.Many2one(check_company=True)
    sequence_id = fields.Many2one(check_company=True)
    sequence_line_id = fields.Many2one(check_company=True)
    pricelist_id = fields.Many2one(check_company=True,
                                   default=_default_pricelist)
    available_pricelist_ids = fields.Many2many(check_company=True)
    tip_product_id = fields.Many2one(check_company=True)
    fiscal_position_ids = fields.Many2many(check_company=True)
    default_fiscal_position_id = fields.Many2one(check_company=True)

    @api.model
    def create(self, vals):
        # If we are creating the pos.config with a specific company, and
        # we are not indicating an invoice journal or location, we
        # propose a default that is consistent with the company provided.
        company_id = vals.get('company_id', False)
        invoice_journal_id = vals.get('invoice_journal_id', False)
        if company_id and not invoice_journal_id:
            invoice_journal = self.with_context(
                company_id=company_id)._default_invoice_journal()
            vals['invoice_journal_id'] = invoice_journal.id
        return super(PosConfig, self).create(vals)

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

    @api.depends('company_id')
    def name_get(self):
        names = super(PosConfig, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
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
        if not self.default_fiscal_position_id.check_company(self.company_id):
            self.default_fiscal_position_id = False
