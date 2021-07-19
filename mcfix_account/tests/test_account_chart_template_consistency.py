# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestAccountChartTemplate(SavepointCase):
    @classmethod
    def with_context(cls, *args, **kwargs):
        context = dict(args[0] if args else cls.env.context, **kwargs)
        cls.env = cls.env(context=context)
        return cls

    @classmethod
    def _get_templates(cls):
        ir_model_data = cls.env["ir.model.data"]

        account_template_data_1 = ir_model_data.search(
            [("name", "=", "transfer_account_id")], limit=1
        )
        account_template_data_2 = ir_model_data.search(
            [("name", "=", "conf_a_recv")], limit=1
        )
        account_template_data_3 = ir_model_data.search(
            [("name", "=", "conf_a_pay")], limit=1
        )

        account_template_1 = cls.env["account.account.template"].browse(
            [account_template_data_1.res_id]
        )
        account_template_2 = cls.env["account.account.template"].browse(
            [account_template_data_2.res_id]
        )
        account_template_3 = cls.env["account.account.template"].browse(
            [account_template_data_3.res_id]
        )

        tax_template_data_1 = ir_model_data.search(
            [("name", "=", "sale_tax_template")], limit=1
        )
        tax_template_data_2 = ir_model_data.search(
            [("name", "=", "purchase_tax_template")], limit=1
        )

        account_tax_template_1 = cls.env["account.tax.template"].browse(
            [tax_template_data_1.res_id]
        )
        account_tax_template_2 = cls.env["account.tax.template"].browse(
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

    @classmethod
    def _chart_of_accounts_create(cls, company, chart, templates):
        cls.env.user.write({"company_ids": [(4, company.id)], "company_id": company.id})
        if not chart:
            return False
        chart.try_loading_for_current_company()
        return True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("base.group_multi_company").write({"users": [(4, cls.env.uid)]})
        # Create companies
        cls.company = cls.env["res.company"].create({"name": "Test company 1"})
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Test company 2", "parent_id": cls.company.id}
        )
        # Create charts
        templates = cls._get_templates()

        cls.chart = cls.env["account.chart.template"].search([], limit=1)

        cls._chart_of_accounts_create(cls.company, cls.chart, templates)

        cls._chart_of_accounts_create(cls.company_2, cls.chart, templates)

        cls.main_partner = cls._create_partner()

    @classmethod
    def _create_partner(cls):
        return cls.env["res.partner"].create(
            {
                "name": "Acme, Inc.",
                "country_id": cls.env.ref("base.us").id,
                "company_id": False,
            }
        )
