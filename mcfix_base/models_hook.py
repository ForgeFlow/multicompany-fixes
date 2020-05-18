# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

from odoo.tools.translate import _
from odoo.models import BaseModel
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def post_load_hook():

    def _new__check_company(self, fnames=None):
        # https://github.com/odoo/odoo/pull/46043
        if fnames is None:
            fnames = self._fields

        regular_fields = []
        property_fields = []
        for name in fnames:
            field = self._fields[name]
            if field.relational and field.check_company and \
                    'company_id' in self.env[field.comodel_name]:
                if not field.company_dependent:
                    regular_fields.append(name)
                else:
                    property_fields.append(name)

        if not (regular_fields or property_fields):
            return

        inconsistent_fields = set()
        inconsistent_recs = self.browse()
        for record in self:
            company = record.company_id \
                if record._name != 'res.company' else record
            for name in regular_fields:
                corecord = record.sudo()[name]

                # ***** changed code start *****
                if not company and corecord._name != self._name:
                    continue
                # ***** changed code end *****

                if corecord._name == 'res.users' and corecord.company_ids:
                    if not (company <= corecord.company_ids):
                        inconsistent_fields.add(name)
                        inconsistent_recs |= record
                elif not (corecord.company_id <= company):
                    inconsistent_fields.add(name)
                    inconsistent_recs |= record

            if self.env.context.get('force_company'):
                company = self.env['res.company'].browse(
                    self.env.context['force_company'])
            else:
                company = self.env.company
            for name in property_fields:
                corecord = record.sudo()[name]
                if corecord._name == 'res.users' and corecord.company_ids:
                    if not (company <= corecord.company_ids):
                        inconsistent_fields.add(name)
                        inconsistent_recs |= record
                elif not (corecord.company_id <= company):
                    inconsistent_fields.add(name)
                    inconsistent_recs |= record

        if inconsistent_fields:
            message = _("""Some records are incompatible with """ +
                        """the company of the %(document_descr)s.

    Incompatibilities:
    Fields: %(fields)s
    Record ids: %(records)s
    """)
            raise UserError(message % {
                'document_descr': self.env['ir.model']._get(self._name).name,
                'fields': ', '.join(sorted(inconsistent_fields)),
                'records': ', '.join(
                    [str(a) for a in inconsistent_recs.ids[:6]]),
            })

    if not hasattr(BaseModel, '_original__check_company'):
        BaseModel._original__check_company = BaseModel._check_company
        BaseModel._check_company = _new__check_company
