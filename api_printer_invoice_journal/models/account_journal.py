# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    """Account Journal"""

    _inherit = "account.journal"

    aps_payment_code = fields.Char(
        string="Payment Code", default="01", size=2, help="Two digits code for fiscal printer (00-25)"
    )
    aps_payment_name = fields.Char(
        string="Payment Name", default="EFECTIVO", size=20, help="Payment name for fiscal printer, use capital letters"
    )

    # API Printer Server Configuration
    aps_ip = fields.Char(
        string="ApiPrinterServer URL",
        default="http://127.0.0.1",
        size=23,
        help="URL, remember to add http:// or https://",
    )

    aps_port = fields.Char(
        string="ApiPrinterServer Port", default="5051", size=4, help="Connection Port, between the port 1024 and 65535"
    )

    aps_default_payment_code = fields.Char(
        string="Default Payment Method Code",
        default="01",
        size=2,
        help="Two digits code for fiscal printer default (00-25)",
    )

    aps_default_payment_name = fields.Char(
        string="Default Payment Method Name",
        default="EFECTIVO",
        size=20,
        help="Payment name for fiscal printer default",
    )

    @api.constrains("aps_default_payment_code", "aps_payment_code")
    def _check_payment_codes(self):
        for record in self:
            for field in ["aps_default_payment_code", "aps_payment_code"]:
                code = getattr(record, field)
                if code and not re.match(r"^([0-1][0-9]|2[0-5])$", code):
                    raise ValidationError(f"{field.replace('_', ' ').title()} must be a number between 00 and 25")
