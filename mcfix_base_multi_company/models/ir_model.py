# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = 'base'

    def _get_companies(self):
        if 'company_ids' in self._fields:
            return self.company_ids
        return super()._get_companies()

    def _company_field_name(self):
        if "company_ids" in self._fields:
            return "company_ids"
        return super()._company_field_name()
