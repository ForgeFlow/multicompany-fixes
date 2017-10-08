# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AssetAssetReport(models.Model):
    _inherit = 'asset.asset.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AssetAssetReport, self).name_get()
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
        self.asset_id = False
        self.asset_category_id = False

    @api.multi
    @api.constrains('asset_id', 'company_id')
    def _check_company_asset_id(self):
        for asset_report in self.sudo():
            if asset_report.company_id and asset_report.asset_id.company_id \
                    and asset_report.company_id != asset_report.asset_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Asset Report and in '
                      'Asset must be the same.'))
        return True

    @api.multi
    @api.constrains('asset_category_id', 'company_id')
    def _check_company_asset_category_id(self):
        for asset_report in self.sudo():
            if asset_report.company_id and asset_report.asset_category_id.\
                    company_id and asset_report.company_id != asset_report.\
                    asset_category_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset Report and in '
                      'Asset category must be the same.'))
        return True
