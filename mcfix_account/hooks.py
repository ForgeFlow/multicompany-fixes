# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Set company_id=False for all account.tax.template records.")

    cr.execute("""
        UPDATE account_tax_template SET company_id=Null
    """)
