# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountJournal, self)._check_company_id()
        for rec in self:
            order = self.env['pos.order'].search(
                [('sale_journal', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sale Journal is assigned to Pos Order '
                      '%s.' % order.name))
            pos_order = self.env['report.pos.order'].search(
                [('journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal is assigned to Pos Order '
                      '%s.' % pos_order.name))
            config = self.env['pos.config'].search(
                [('journal_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Payment Method is assigned to Pos Config '
                      '%s.' % config.name))
            config = self.env['pos.config'].search(
                [('journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sale Journal is assigned to Pos Config '
                      '%s.' % config.name))
            config = self.env['pos.config'].search(
                [('invoice_journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice Journal is assigned to Pos Config '
                      '%s.' % config.name))
