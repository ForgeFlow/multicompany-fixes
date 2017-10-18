# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountReconcileModel, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        for reconcile in self:
            reconcile.account_id = False
            reconcile.journal_id = False
            reconcile.tax_id = False
            reconcile.analytic_account_id = False
            reconcile.second_account_id = False
            reconcile.second_journal_id = False
            reconcile.second_tax_id = False
            reconcile.second_analytic_account_id = False

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.account_id.company_id and
                reconcile.company_id != reconcile.account_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.journal_id.company_id and
                reconcile.company_id != reconcile.journal_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_id', 'company_id')
    def _check_company_tax_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.tax_id.company_id and
                reconcile.company_id != reconcile.tax_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('analytic_account_id', 'company_id')
    def _check_company_analytic_account_id(self):
        for reconcile_model in self.sudo():
            if reconcile_model.company_id and reconcile_model.\
                    analytic_account_id.company_id and \
                    reconcile_model.company_id != reconcile_model.\
                    analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Reconciliation Model and in '
                      'Analytic Account must be the same.'))
        return True

    @api.multi
    @api.constrains('second_account_id', 'company_id')
    def _check_company_second_account_id(self):
        for reconcile_model in self.sudo():
            if reconcile_model.company_id and reconcile_model.\
                    second_account_id.company_id and \
                    reconcile_model.company_id != reconcile_model.\
                    second_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Reconciliation Model and in '
                      'Second Account must be the same.'))
        return True

    @api.multi
    @api.constrains('second_journal_id', 'company_id')
    def _check_company_second_journal_id(self):
        for reconcile_model in self.sudo():
            if reconcile_model.company_id and reconcile_model.\
                    second_journal_id.company_id and \
                    reconcile_model.company_id != reconcile_model.\
                    second_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Reconciliation Model and in '
                      'Second Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('second_tax_id', 'company_id')
    def _check_company_second_tax_id(self):
        for reconcile_model in self.sudo():
            if reconcile_model.company_id and reconcile_model.second_tax_id.\
                    company_id and reconcile_model.company_id != \
                    reconcile_model.second_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Reconciliation Model and in '
                      'Second Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('second_analytic_account_id', 'company_id')
    def _check_company_second_analytic_account_id(self):
        for reconcile_model in self.sudo():
            if reconcile_model.company_id and reconcile_model.\
                    second_analytic_account_id.company_id and \
                    reconcile_model.company_id != reconcile_model.\
                    second_analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Reconciliation Model and in '
                      'Second Analytic Account must be the same.'))
        return True


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountPartialReconcile, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.debit_move_id = False
        self.credit_move_id = False

    @api.multi
    @api.constrains('debit_move_id', 'company_id')
    def _check_company_debit_move_id(self):
        for partial_reconcile in self.sudo():
            if partial_reconcile.company_id and partial_reconcile.\
                    debit_move_id.company_id and partial_reconcile.company_id \
                    != partial_reconcile.debit_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Partial Reconcile and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('credit_move_id', 'company_id')
    def _check_company_credit_move_id(self):
        for partial_reconcile in self.sudo():
            if partial_reconcile.company_id and partial_reconcile.\
                    credit_move_id.company_id and partial_reconcile.company_id\
                    != partial_reconcile.credit_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Partial Reconcile and in '
                      ' must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
            pass
