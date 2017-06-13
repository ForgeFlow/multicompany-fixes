from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        team = self.env['crm.team']._get_default_team_id()
        if team.company_id:
            rec.update({
                'company_id': team.company_id.id})
        return rec

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        self.ensure_one()
        journal_id = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id)], limit=1)
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals['account_id'] = self.with_context(
            force_company=self.company_id.id).partner_invoice_id.property_account_receivable_id.id
        invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id or self.with_context(
            force_company=self.company_id.id).partner_invoice_id.property_account_position_id.id
        invoice_vals['journal_id'] = journal_id.ensure_one().id
        return invoice_vals

    @api.multi
    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        self.fiscal_position_id = self.with_context(force_company=self.company_id.id).env[
            'account.fiscal.position'].get_fiscal_position(self.partner_id.id,
                                                           self.partner_shipping_id.id)
        for line in self.order_line:
            line.change_company()
        return {}

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_team_company(self):
        for rec in self:
            if (rec.team_id and rec.team_id.company_id and
                    rec.team_id.company_id != rec.company_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Company of the sales team '
                                        'must match with that of the '
                                        'quote/sales order'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('company_id')
    def change_company(self):
        self._compute_tax_id()

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        :param qty: float quantity to invoice
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        self.ensure_one()
        account = self.with_context(
            force_company=self.company_id.id).product_id.property_account_income_id or self.with_context(
            force_company=self.company_id.id).product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.with_context(
            force_company=self.company_id.id).order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)
        res['account_id'] = account.id
        return res
