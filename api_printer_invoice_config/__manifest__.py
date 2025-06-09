# -*- coding: utf-8 -*-
{
    "name": "API Printer Invoice",
    "summary": """Module to communicate with a printing program via REST API""",
    "description": """This module provides an integration between Odoo and a fiscal printer through a REST API.
        * Printing of tax invoices / credit notes / debit notes
        * Handling of discounts and notes on products
        * Tax reports (X/Z) 
        * Support for multiple currencies and exchange rates
        
        The module is designed to work with Venezuelan fiscal printers and complies with the 
        following requirements local fiscal requirements.""",
    "category": "Accounting",
    "version": "17.0.2.7",
    "author": "eyngroupdev@gmail.com",
    "maintainer": "iron.graterol@gmail.com",
    "website": "https://eyngroup.odoo.com",
    "license": "AGPL-3",
    "depends": ["account", "web"],
    "data": [
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "views/account_journal_views.xml",
        "views/fiscal_report_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "api_printer_invoice/static/src/js/account_printer.js",
            "api_printer_invoice/static/src/js/fiscal_report.js",
            "api_printer_invoice/static/src/xml/fiscal_report.xml",
        ],
    },
    "application": False,
    "installable": True,
}
