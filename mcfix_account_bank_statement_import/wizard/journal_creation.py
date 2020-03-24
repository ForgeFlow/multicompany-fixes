from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBankStatementImportJournalCreation(models.TransientModel):
    _inherit = 'account.bank.statement.import.journal.creation'

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'loss_account_id')
    def _check_company_id_loss_account_id(self):
        for rec in self.sudo():
            if not rec.loss_account_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'default_debit_account_id')
    def _check_company_id_default_debit_account_id(self):
        for rec in self.sudo():
            if not rec.default_debit_account_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'sequence_id')
    def _check_company_id_sequence_id(self):
        for rec in self.sudo():
            if not rec.sequence_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Ir Sequence must be the same.'))

    @api.multi
    @api.constrains('company_id', 'profit_account_id')
    def _check_company_id_profit_account_id(self):
        for rec in self.sudo():
            if not rec.profit_account_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_control_ids')
    def _check_company_id_account_control_ids(self):
        for rec in self.sudo():
            for line in rec.account_control_ids:
                if not line.check_company(rec):
                    raise ValidationError(
                        _('The Company in the '
                          'Account Bank Statement Import Journal Creation '
                          'and in Account Account (%s) must be '
                          'the same.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'refund_sequence_id')
    def _check_company_id_refund_sequence_id(self):
        for rec in self.sudo():
            if not rec.refund_sequence_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Ir Sequence must be the same.'))

    @api.multi
    @api.constrains('company_id', 'bank_account_id')
    def _check_company_id_bank_account_id(self):
        for rec in self.sudo():
            if not rec.bank_account_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Res Partner Bank must be the same.'))

    @api.multi
    @api.constrains('company_id', 'default_credit_account_id')
    def _check_company_id_default_credit_account_id(self):
        for rec in self.sudo():
            if not rec.default_credit_account_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the '
                      'Account Bank Statement Import Journal Creation and in '
                      'Account Account must be the same.'))
