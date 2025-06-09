# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    """Res Config Settings"""

    _inherit = "res.config.settings"

    aps_ip = fields.Char(
        string="ApiPrinterServer URL",
        default="http://127.0.0.1",
        size=23,
        help="URL, remember to add http:// or https://",
        config_parameter="aps_ip",
    )

    aps_port = fields.Char(
        string="ApiPrinterServer Port",
        default="5051",
        size=4,
        help="Connection Port, between the port 1024 and 65535",
        config_parameter="aps_port",
    )

    aps_default_payment_code = fields.Char(
        string="Default Payment Method Code",
        default="01",
        size=2,
        help="Two digits code for fiscal printer default (00-25)",
        config_parameter="aps_default_payment_code",
    )

    aps_default_payment_name = fields.Char(
        string="Default Payment Method Name",
        default="CASH",
        size=20,
        help="Payment name for fiscal printer default",
        config_parameter="aps_default_payment_name",
    )

    @api.constrains("aps_default_payment_code")
    def _check_payment_code(self):
        for record in self:
            if record.aps_default_payment_code:
                if not re.match(r"^([0-1][0-9]|2[0-5])$", record.aps_default_payment_code):
                    raise ValidationError("Payment Code must be a number between 00 and 25")
