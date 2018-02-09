from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.multi
    def write(self, vals):
        for journal in self:
            if 'company_id' in vals:
                if journal.check_sequence_id.company_id.id != vals[
                        'company_id']:
                    journal.check_sequence_id.with_context(
                        bypass_company_validation=True).sudo().write(
                        {'company_id': vals['company_id']})
        return super(AccountJournal, self).write(vals)

    @api.multi
    @api.constrains('company_id', 'check_sequence_id')
    def _check_company_id_check_sequence_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.check_sequence_id.company_id and\
                    rec.company_id != rec.check_sequence_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Journal and in '
                      'Ir Sequence must be the same.'))
