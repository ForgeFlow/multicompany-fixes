from odoo import models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    @api.depends('name', 'currency_id', 'company_id', 'company_id.currency_id')
    def name_get(self):
        res = []
        journal_names = super(AccountJournal, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return journal_names
        for journal_name in journal_names:
            journal = self.browse(journal_name[0])
            name = "%s [%s]" % (journal_name[1], journal.company_id.name)
            res += [(journal.id, name)]
        return res
