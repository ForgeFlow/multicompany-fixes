from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        if not so_line.company_id:
            so_line.company_id = order.company_id
        return super(SaleAdvancePaymentInv, self.with_context(
            force_company=order.company_id.id,
            default_company_id=order.company_id.id,
            company_id=order.company_id.id,
        ))._create_invoice(order.with_context(
            force_company=order.company_id.id
        ), so_line.with_context(
            force_company=order.company_id.id
        ), amount)
