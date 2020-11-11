import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Create and fill company_id column in database")
    cr.execute("""
        ALTER TABLE stock_move_line ADD COLUMN IF NOT EXISTS company_id integer;
    """)
    cr.execute("""
        UPDATE stock_move_line sml
        SET company_id = sm.company_id
        FROM stock_move sm
        WHERE sml.move_id = sm.id AND sml.company_id IS  NULL
    """)
