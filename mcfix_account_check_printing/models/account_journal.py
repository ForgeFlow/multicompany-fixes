from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_sequence_id = fields.Many2one(check_company=True)

    def write(self, vals):
        for journal in self:
            if 'company_id' in vals:
                if journal.check_sequence_id.company_id.id != vals[
                        'company_id']:
                    journal.check_sequence_id.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
        return super(AccountJournal, self).write(vals)
