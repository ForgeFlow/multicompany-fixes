from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.journal_id.check_company(self.company_id):
            self._cache.update(self._convert_to_cache(
                {'journal_id': False}, update=True))
        if not self.account_asset_id.check_company(self.company_id):
            self._cache.update(self._convert_to_cache(
                {'account_asset_id': False}, update=True))
        if not self.account_depreciation_id.check_company(self.company_id):
            self._cache.update(self._convert_to_cache(
                {'account_depreciation_id': False}, update=True))
        if not self.account_depreciation_expense_id.check_company(
            self.company_id
        ):
            self._cache.update(self._convert_to_cache(
                {'account_depreciation_expense_id': False}, update=True))
        if not self.account_analytic_id.check_company(self.company_id):
            self.account_analytic_id = False

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_depreciation_id')
    def _check_company_id_account_depreciation_id(self):
        for rec in self.sudo():
            if not rec.account_depreciation_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_depreciation_expense_id')
    def _check_company_id_account_depreciation_expense_id(self):
        for rec in self.sudo():
            if not rec.account_depreciation_expense_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_asset_id')
    def _check_company_id_account_asset_id(self):
        for rec in self.sudo():
            if not rec.account_asset_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.asset.asset', [('category_id', '=', self.id)]),
            ('account.invoice.line', [('asset_category_id', '=', self.id)]),
        ]
        return res


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.category_id.check_company(self.company_id):
            self._cache.update(self._convert_to_cache(
                {'category_id': False}, update=True))
        if not self.invoice_id.check_company(self.company_id):
            self.invoice_id = False
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if not rec.invoice_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'category_id')
    def _check_company_id_category_id(self):
        for rec in self.sudo():
            if not rec.category_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Account Asset Category must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('asset.asset.report', [('asset_id', '=', self.id)]),
        ]
        return res
