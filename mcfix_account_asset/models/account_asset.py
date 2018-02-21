from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.journal_id.company_id and \
                self.journal_id.company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'journal_id': False}, update=True))
        if self.company_id and self.account_asset_id.company_id and \
                self.account_asset_id.company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'account_asset_id': False}, update=True))
        if self.company_id and self.account_depreciation_id.company_id and \
                self.account_depreciation_id.company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'account_depreciation_id': False}, update=True))
        if self.company_id and self.account_depreciation_expense_id.\
                company_id and self.account_depreciation_expense_id.\
                company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'account_depreciation_expense_id': False}, update=True))
        if self.company_id and self.account_analytic_id.company_id and \
                self.account_analytic_id.company_id != self.company_id:
            self.account_analytic_id = False

    @api.multi
    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_analytic_id.company_id and\
                    rec.company_id != rec.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_depreciation_id')
    def _check_company_id_account_depreciation_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_depreciation_id.company_id and\
                    rec.company_id != rec.account_depreciation_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_depreciation_expense_id')
    def _check_company_id_account_depreciation_expense_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_depreciation_expense_id.\
                    company_id and rec.company_id != rec.\
                    account_depreciation_expense_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_asset_id')
    def _check_company_id_account_asset_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_asset_id.company_id and\
                    rec.company_id != rec.account_asset_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Category and in '
                      'Account Account must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.asset.asset'].search(
                    [('category_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Asset Category is assigned to '
                          'Account Asset Asset (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['asset.asset.report'].search(
                    [('asset_category_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Asset Category is assigned to '
                          'Asset Asset Report (%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.line'].search(
                    [('asset_category_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Asset Category is assigned to '
                          'Account Invoice Line (%s)'
                          '.' % field.name_get()[0][1]))


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.multi
    def _compute_entries(self, date, group_entries=False):
        return super(AccountAssetAsset, self.with_context(
            default_company_id=self.company_id.id))._compute_entries(
            date=date, group_entries=group_entries)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.category_id.company_id and \
                self.category_id.company_id != self.company_id:
            self._cache.update(self._convert_to_cache(
                {'category_id': False}, update=True))
        if self.company_id and self.invoice_id.company_id and \
                self.invoice_id.company_id != self.company_id:
            self.invoice_id = False
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = False

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.invoice_id.company_id and\
                    rec.company_id != rec.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'category_id')
    def _check_company_id_category_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.category_id.company_id and\
                    rec.company_id != rec.category_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Asset Asset and in '
                      'Account Asset Category must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['asset.asset.report'].search(
                    [('asset_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Asset Asset is assigned to '
                          'Asset Asset Report (%s).' % field.name_get()[0][1]))


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        moves = []
        for line in self:
            moves += super(AccountAssetDepreciationLine, line.with_context(
                default_company_id=line.asset_id.company_id.id
            )).create_move(post_move=post_move)
        return moves
