# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountVoucher, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.journal_id = False
        self.account_id = False
        self.move_id = False

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.journal_id and \
                    voucher.company_id != voucher.journal_id.company_id:
                raise ValidationError(_('The Company in the Voucher and in '
                                        ' must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.account_id and \
                    voucher.company_id != voucher.account_id.company_id:
                raise ValidationError(_('The Company in the Voucher and in '
                                        ' must be the same.'))
        return True

    @api.multi
    @api.constrains('move_id', 'company_id')
    def _check_company_move_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.move_id and \
                    voucher.company_id != voucher.move_id.company_id:
                raise ValidationError(_('The Company in the Voucher and in '
                                        ' must be the same.'))
        return True
