from odoo import models, fields, api


class FiscalReportWizard(models.TransientModel):
    _name = "fiscal.report.wizard"
    _description = "Fiscal Report Wizard"

    journal_id = fields.Many2one(
        "account.journal", string="Sales Journal", domain=[("type", "=", "sale")], required=True
    )
    report_type = fields.Selection([("x", "Report X"), ("z", "Report Z")], string="Report Type", required=True)

    def print_report(self):
        return {
            "type": "ir.actions.client",
            "tag": "fiscal_report",
            "params": {
                "report_type": self.report_type,
                "journal_id": self.journal_id.id,
                "url": f"{self.journal_id.aps_ip}:{self.journal_id.aps_port}/api/printers",
            },
        }
