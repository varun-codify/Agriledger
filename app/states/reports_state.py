import reflex as rx
import datetime
import os
import logging
from app.states.transaction_state import TransactionState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import openpyxl
except ImportError as e:
    logging.exception(f"Optional dependencies missing: {e}")


class ReportsState(rx.State):
    """Manages report generation and data aggregation."""

    date_range: str = "Last 30 Days"
    custom_start_date: str = (
        datetime.date.today() - datetime.timedelta(days=30)
    ).isoformat()
    custom_end_date: str = datetime.date.today().isoformat()
    generated_file_url: str = ""
    show_download_link: bool = False

    @rx.var
    def total_income(self) -> float:
        return 15000.0

    @rx.var
    def total_expenses(self) -> float:
        return 8500.0

    @rx.var
    def net_profit(self) -> float:
        return self.total_income - self.total_expenses

    @rx.var
    def expense_by_category(self) -> list[dict]:
        return [
            {"name": "Feed", "value": 4500},
            {"name": "Labor", "value": 2000},
            {"name": "Medicine", "value": 1500},
            {"name": "Utilities", "value": 500},
        ]

    @rx.event
    def set_date_range(self, range_val: str):
        self.date_range = range_val
        today = datetime.date.today()
        if range_val == "Last 30 Days":
            self.custom_start_date = (today - datetime.timedelta(days=30)).isoformat()
            self.custom_end_date = today.isoformat()
        elif range_val == "Last Month":
            first = today.replace(day=1)
            last_month = first - datetime.timedelta(days=1)
            self.custom_end_date = last_month.isoformat()
            self.custom_start_date = last_month.replace(day=1).isoformat()
        elif range_val == "This Year":
            self.custom_start_date = today.replace(month=1, day=1).isoformat()
            self.custom_end_date = today.isoformat()

    @rx.event
    async def generate_pdf_report(self):
        """Generates a PDF report."""
        try:
            filename = f"report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            c = canvas.Canvas(file_path, pagesize=letter)
            c.drawString(100, 750, "AgriLedger Farm Report")
            c.drawString(
                100,
                730,
                f"Date Range: {self.custom_start_date} to {self.custom_end_date}",
            )
            c.drawString(100, 700, "Financial Summary")
            c.drawString(100, 680, f"Total Income: ${self.total_income}")
            c.drawString(100, 660, f"Total Expenses: ${self.total_expenses}")
            c.drawString(100, 640, f"Net Profit: ${self.net_profit}")
            c.save()
            self.generated_file_url = f"/_upload/{filename}"
            return rx.download(url=self.generated_file_url, filename=filename)
        except Exception as e:
            logging.exception(f"Error generating PDF: {e}")
            return rx.toast.error(f"Error generating PDF: {str(e)}")

    @rx.event
    async def generate_excel_report(self):
        """Generates an Excel report."""
        try:
            filename = f"report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Financial Summary"
            ws.append(["AgriLedger Report"])
            ws.append(
                ["Date Range", f"{self.custom_start_date} to {self.custom_end_date}"]
            )
            ws.append([])
            ws.append(["Metric", "Value"])
            ws.append(["Total Income", self.total_income])
            ws.append(["Total Expenses", self.total_expenses])
            ws.append(["Net Profit", self.net_profit])
            wb.save(file_path)
            self.generated_file_url = f"/_upload/{filename}"
            return rx.download(url=self.generated_file_url, filename=filename)
        except Exception as e:
            logging.exception(f"Error generating Excel: {e}")
            return rx.toast.error(f"Error generating Excel: {str(e)}")