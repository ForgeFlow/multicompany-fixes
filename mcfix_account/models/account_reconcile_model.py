from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

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
                reconcile.company_id
                and reconcile.account_id.company_id
                and reconcile.company_id != reconcile.account_id.company_id
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
                reconcile.company_id
                and reconcile.journal_id.company_id
                and reconcile.company_id != reconcile.journal_id.company_id
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
                reconcile.company_id
                and reconcile.tax_id.company_id
                and reconcile.company_id != reconcile.tax_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Tax must be the same.'))
        return True


