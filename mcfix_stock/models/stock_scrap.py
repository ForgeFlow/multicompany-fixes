from odoo import models


class StockScrap(models.Model):
    _inherit = "stock.scrap"
    _check_company_auto = True
