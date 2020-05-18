from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    _check_company_auto = True

    journal_id = fields.Many2one(
        check_company=True, domain="[('id', 'in', suitable_journal_ids)]")
    suitable_journal_ids = fields.Many2many(
        comodel_name='account.journal',
        compute='_compute_suitable_journal_ids')
    partner_id = fields.Many2one(check_company=True)
    reversed_entry_id = fields.Many2one(
        check_company=True)
    fiscal_position_id = fields.Many2one(check_company=True)
    invoice_payment_term_id = fields.Many2one(
        check_company=True)
    invoice_partner_bank_id = fields.Many2one(check_company=True)
    invoice_vendor_bill_id = fields.Many2one(check_company=True)
    company_id = fields.Many2one(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    tax_cash_basis_rec_id = fields.Many2one(check_company=True)

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            domain = [('company_id', '=', m.company_id.id), (
                'type', '=?', m.invoice_filter_type_domain)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.model_create_multi
    def create(self, mvals):
        for vals in mvals:
            if vals.get('journal_id', False) and \
                    not vals.get('company_id', False):
                vals['company_id'] = self.env['account.journal'].browse(
                    vals['journal_id']).company_id.id
        return super().create(mvals)

    def write(self, vals):
        if vals.get('journal_id', False):
            vals['company_id'] = self.env['account.journal'].browse(
                vals['journal_id']).company_id.id
        return super().write(vals)

    @api.depends('company_id')
    def name_get(self):
        names = super(AccountMove, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        default = self.env.context['default_journal_type']
        for record in self:
            record.journal_id = self.env['account.journal'].search([
                ('company_id', '=', record.company_id.id),
                ('type', '=', default)
            ], limit=1).id
            record.line_ids = False

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.line_ids, ]
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _check_company_auto = True

    move_id = fields.Many2one(check_company=True)
    account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=True)
    reconcile_model_id = fields.Many2one(check_company=True)
    payment_id = fields.Many2one(check_company=True)
    statement_line_id = fields.Many2one(check_company=True)
    tax_ids = fields.Many2many(check_company=True)
    tax_repartition_line_id = fields.Many2one(check_company=True)
    analytic_account_id = fields.Many2one(check_company=True)
    analytic_tag_ids = fields.Many2many(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    product_id = fields.Many2one(check_company=True)

    @api.depends('company_id')
    def name_get(self):
        names = super(AccountMoveLine, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.analytic_line_ids,
            self.matched_debit_ids,
            self.matched_credit_ids,
        ]
        return res
