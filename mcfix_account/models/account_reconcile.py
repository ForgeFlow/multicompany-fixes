from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    @api.multi
    @api.constrains('company_id', 'credit_move_id')
    def _check_company_id_credit_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.credit_move_id.company_id and\
                    rec.company_id != rec.credit_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Partial Reconcile and in '
                      'Account Move Line must be the same.'))

    @api.multi
    @api.constrains('company_id', 'debit_move_id')
    def _check_company_id_debit_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.debit_move_id.company_id and\
                    rec.company_id != rec.debit_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Partial Reconcile and in '
                      'Account Move Line must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res.append(self.env['account.move'].search(
            [('tax_cash_basis_rec_id', '=', self.id)]))
        return res


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.tax_id.company_id and \
                self.tax_id.company_id != self.company_id:
            self.tax_id = False
        if self.company_id and self.account_id.company_id and \
                self.account_id.company_id != self.company_id:
            if self.tax_id.account_id:
                self.account_id = self.tax_id.account_id
            else:
                self.account_id = False
        if self.company_id and self.journal_id.company_id and \
                self.journal_id.company_id != self.company_id:
            self.journal_id = False
        if self.company_id and self.analytic_account_id.company_id and \
                self.analytic_account_id.company_id != self.company_id:
            self.analytic_account_id = False
        if self.company_id and self.second_tax_id.company_id and \
                self.second_tax_id.company_id != self.company_id:
            self.second_tax_id = False
        if self.company_id and self.second_account_id.company_id and \
                self.second_account_id.company_id != self.company_id:
            self.second_account_id = False
        if self.company_id and self.second_journal_id.company_id and \
                self.second_journal_id.company_id != self.company_id:
            self.second_journal_id = False
        if self.company_id and self.second_analytic_account_id.company_id and \
                self.second_analytic_account_id.company_id != self.company_id:
            self.second_analytic_account_id = False

    @api.multi
    @api.constrains('company_id', 'second_analytic_account_id')
    def _check_company_id_second_analytic_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.second_analytic_account_id.company_id \
                    and rec.company_id != rec.second_analytic_account_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'second_account_id')
    def _check_company_id_second_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.second_account_id.company_id and\
                    rec.company_id != rec.second_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'second_journal_id')
    def _check_company_id_second_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.second_journal_id.company_id and\
                    rec.company_id != rec.second_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_id')
    def _check_company_id_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_id.company_id and\
                    rec.company_id != rec.tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'second_tax_id')
    def _check_company_id_second_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.second_tax_id.company_id and\
                    rec.company_id != rec.second_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'analytic_account_id')
    def _check_company_id_analytic_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.analytic_account_id.company_id and\
                    rec.company_id != rec.analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Reconcile Model and in '
                      'Account Journal must be the same.'))
