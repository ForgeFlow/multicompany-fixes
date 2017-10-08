# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PaymentAcquirer, self).name_get()
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
        self.journal_id = False

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for acquirer in self.sudo():
            if acquirer.company_id and acquirer.journal_id.company_id and \
                    acquirer.company_id != acquirer.journal_id.company_id:
                raise ValidationError(_('The Company in the Payment Acquirer '
                                        'and in Journal must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            pass
