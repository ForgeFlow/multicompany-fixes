# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAccountChartTemplate(TransactionCase):
    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def _get_templates(self):
        ir_model_data = self.env["ir.model.data"]

        account_template_data_1 = ir_model_data.search(
            [("name", "=", "transfer_account_id")], limit=1
        )
        account_template_data_2 = ir_model_data.search(
            [("name", "=", "conf_a_recv")], limit=1
        )
        account_template_data_3 = ir_model_data.search(
            [("name", "=", "conf_a_pay")], limit=1
        )

        account_template_1 = self.env["account.account.template"].browse(
            [account_template_data_1.res_id]
        )
        account_template_2 = self.env["account.account.template"].browse(
            [account_template_data_2.res_id]
        )
        account_template_3 = self.env["account.account.template"].browse(
            [account_template_data_3.res_id]
        )

        tax_template_data_1 = ir_model_data.search(
            [("name", "=", "sale_tax_template")], limit=1
        )
        tax_template_data_2 = ir_model_data.search(
            [("name", "=", "purchase_tax_template")], limit=1
        )

        account_tax_template_1 = self.env["account.tax.template"].browse(
            [tax_template_data_1.res_id]
        )
        account_tax_template_2 = self.env["account.tax.template"].browse(
            [tax_template_data_2.res_id]
        )

        res = [
            account_template_1,
            account_template_2,
            account_template_3,
            account_tax_template_1,
            account_tax_template_2,
        ]
        return res

    def _chart_of_accounts_create(self, company, chart, templates):
        self.env.user.write(
            {"company_ids": [(4, company.id)], "company_id": company.id}
        )
        if not chart:
            return False
        chart.try_loading_for_current_company()
        return True

    def setUp(self):
        super(TestAccountChartTemplate, self).setUp()
        self.env.ref("base.group_multi_company").write({"users": [(4, self.env.uid)]})
        # Create companies
        self.company = self.env["res.company"].create({"name": "Test company 1"})
        self.company_2 = self.env["res.company"].create(
            {"name": "Test company 2", "parent_id": self.company.id}
        )
        # Create charts
        templates = self._get_templates()

        self.chart = self.env["account.chart.template"].search([], limit=1)

        self._chart_of_accounts_create(self.company, self.chart, templates)

        self._chart_of_accounts_create(self.company_2, self.chart, templates)

        self.main_partner = self._create_partner()

    def _create_partner(self):
        return self.env["res.partner"].create(
            {
                "name": "Acme, Inc.",
                "country_id": self.env.ref("base.us").id,
                "company_id": False,
            }
        )
