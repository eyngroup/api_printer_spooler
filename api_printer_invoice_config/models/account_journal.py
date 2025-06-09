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

    @api.constrains("aps_payment_code")
    def _check_payment_code(self):
        for record in self:
            if record.aps_payment_code:
                if not re.match(r"^([0-1][0-9]|2[0-5])$", record.aps_payment_code):
                    raise ValidationError("Payment Code must be a number between 00 and 25")
