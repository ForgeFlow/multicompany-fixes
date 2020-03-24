# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging
from odoo import api, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = 'base'

    def add_company_suffix(self, names):
        res = []
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id or \
                self._context.get('not_display_company'):
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.sudo().name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        """When the user is assigned to the multi-company group,
        all of the multi-company dependent objects will be listed with the
        company as suffix, in brackets."""
        names = super(Base, self).name_get()
        if 'company_id' not in self._fields:
            return names
        res = self.add_company_suffix(names)
        return res

    def _get_companies(self):
        if 'company_id' in self._fields:
            return self.company_id
        return self.env['res.company']

    def _check_company(self, element):
        if 'company_id' not in self._fields:
            return self.browse()
        company_id = element._get_companies()
        if not company_id:
            return self.browse()
        result = self.browse()
        for record in self:
            record_companies = record._get_companies()
            if not record_companies:
                continue
            if not any(c in company_id for c in record_companies):
                result |= record
        return result

    def _old_check_company(self, company_id):
        """This method will be used in constrains methods
        to ensure consistency between linked many2one models company-wise.
        Typically when the method returns false a Validation Error
        will be raised."""
        if not company_id:
            return self.browse()
        if 'company_id' not in self._fields:
            return self.browse()
        return self.filtered(
            lambda r: r.company_id and r.company_id != company_id)

    def check_company(self, company_id):
        return not bool(self._check_company(company_id))

    def _check_company_id_fields(self):
        return []

    def _check_company_id_search(self):
        return []

    def _check_company_id_base_model(self):
        """This method is to be used in constrains methods of
        company-dependent models to ensure consistency between the model
        other company-dependent linked models, that are either provided
        as one2many in the first model, or where the other models reference
        the first model in some field."""
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self.sudo():
                if not rec.company_id:
                    continue
                fields = rec._check_company_id_fields()
                for model, domain in rec._check_company_id_search():
                    fields.append(self.sudo().env[model].search(domain + [
                        ('company_id', '!=', rec.company_id.id),
                        ('company_id', '!=', False),
                    ], limit=1))
                for fld in fields:
                    issues = fld._check_company(rec.company_id)
                    if issues:
                        raise ValidationError(_(
                            'You cannot change the company, as this %s (%s) '
                            'is assigned to %s (%s).'
                        ) % (
                            rec._name, rec.display_name,
                            fld._name, ', '.join(issues.mapped('display_name'))
                        ))
