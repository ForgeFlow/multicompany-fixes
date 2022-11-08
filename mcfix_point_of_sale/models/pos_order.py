# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _default_company(self):
        return self._default_session().config_id.company_id

    def _default_session(self):
        super(PosOrder, self)._default_session()
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        return self.env['pos.session'].search(
            [('state', '=', 'opened'), ('user_id', '=', self.env.uid),
             ('config_id.company_id', '=', company_id)], limit=1)

    # We override the default in order to provide a default company that is
    # consistent with the default session.
    company_id = fields.Many2one(default=_default_company)

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', False)
        session_id = vals.get('session_id', False)

        # If we are creating the pos.order with a session but not a company,
        # we propose a company that is consistent with the session provided.
        if session_id and not company_id:
            session = self.env['pos.session'].browse(session_id)
            vals['company_id'] = session.config_id.company_id.id

        # If we are creating the pos.order with a specific company but
        # not a session, we propose a default session that is consistent with
        # the company provided.
        if company_id and not session_id:
            session = self.with_context(
                company_id=company_id)._default_session()
            if session:
                vals['session_id'] = session.id
        return super(PosOrder, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.pricelist_id.check_company(self.company_id):
            self.pricelist_id = self.config_id.pricelist_id

    @api.multi
    @api.constrains('company_id', 'account_move')
    def _check_company_id_account_move(self):
        for rec in self.sudo():
            if not rec.account_move.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'fiscal_position_id')
    def _check_company_id_fiscal_position_id(self):
        for rec in self.sudo():
            if not rec.fiscal_position_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Fiscal Position must be the same.'))

    @api.multi
    @api.constrains('company_id', 'picking_id')
    def _check_company_id_picking_id(self):
        for rec in self.sudo():
            if not rec.picking_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Stock Picking must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if not rec.invoice_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Pos Order and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'pricelist_id')
    def _check_company_id_pricelist_id(self):
        for rec in self.sudo():
            if not rec.pricelist_id.check_company(rec):
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

    company_id = fields.Many2one(
        related='order_id.company_id', default=False, readonly=True,
    )

    @api.multi
    @api.constrains('tax_ids')
    def _check_company_id_tax_ids(self):
        for rec in self.sudo():
            for line in rec.tax_ids:
                if not line.check_company(rec):
                    raise ValidationError(
                        _('The Company in the Pos Order Line and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.name_get()[0][1])
