# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountConfigSettings, self).name_get()
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
        self.chart_template_id = False
        self.sale_tax_id = False
        self.purchase_tax_id = False
        self.transfer_account_id = False
        self.currency_exchange_journal_id = False
        self.default_sale_tax_id = False
        self.default_purchase_tax_id = False

    @api.multi
    @api.constrains('chart_template_id', 'company_id')
    def _check_company_chart_template_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.\
                    chart_template_id.company_id and config_settings.\
                    company_id != config_settings.chart_template_id.company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Template must be the same.'))
        return True

    @api.multi
    @api.constrains('sale_tax_id', 'company_id')
    def _check_company_sale_tax_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.sale_tax_id.\
                    company_id and config_settings.company_id != \
                    config_settings.sale_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Default sale tax must be the same.'))
        return True

    @api.multi
    @api.constrains('purchase_tax_id', 'company_id')
    def _check_company_purchase_tax_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.purchase_tax_id.\
                    company_id and config_settings.company_id != \
                    config_settings.purchase_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Default purchase tax must be the same.'))
        return True

    @api.multi
    @api.constrains('transfer_account_id', 'company_id')
    def _check_company_transfer_account_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.\
                    transfer_account_id.company_id and config_settings.\
                    company_id != config_settings.transfer_account_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('currency_exchange_journal_id', 'company_id')
    def _check_company_currency_exchange_journal_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.\
                    currency_exchange_journal_id.company_id and \
                    config_settings.company_id != config_settings.\
                    currency_exchange_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Rate Difference Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('default_sale_tax_id', 'company_id')
    def _check_company_default_sale_tax_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.\
                    default_sale_tax_id.company_id and config_settings.\
                    company_id != config_settings.default_sale_tax_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Default Sale Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('default_purchase_tax_id', 'company_id')
    def _check_company_default_purchase_tax_id(self):
        for config_settings in self.sudo():
            if config_settings.company_id and config_settings.\
                    default_purchase_tax_id.company_id and \
                    config_settings.company_id != config_settings.\
                    default_purchase_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Config Settings and in '
                      'Default Purchase Tax must be the same.'))
        return True
