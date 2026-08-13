import datetime
import logging

import reflex as rx

try:
    import openpyxl
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError as e:
    logging.exception(f"Optional dependencies missing: {e}")

from app.states.transaction_state import TransactionState


class ReportsState(rx.State):
    """Manages report generation and data aggregation (computed from real transactions)."""

    date_range: str = "Last 30 Days"
    custom_start_date: str = (
        datetime.date.today() - datetime.timedelta(days=30)
    ).isoformat()
    custom_end_date: str = datetime.date.today().isoformat()
    generated_file_url: str = ""
    show_download_link: bool = False

    def _transactions_in_range(self, transactions: list[dict]) -> list[dict]:
        """Filter transactions by the selected date range."""
        start = self.custom_start_date
        end = self.custom_end_date
        return [
            tx
            for tx in transactions
            if start <= tx.get("date", "") <= end
        ]

    @rx.var
    async def total_income(self) -> float:
        ts = await self.get_state(TransactionState)
        return sum(
            float(tx["amount"])
            for tx in self._transactions_in_range(ts.transactions)
            if tx["type"] == "income"
        )

    @rx.var
    async def total_expenses(self) -> float:
        ts = await self.get_state(TransactionState)
        return sum(
            float(tx["amount"])
            for tx in self._transactions_in_range(ts.transactions)
            if tx["type"] == "expense"
        )

    @rx.var
    async def net_profit(self) -> float:
        ts = await self.get_state(TransactionState)
        in_range = self._transactions_in_range(ts.transactions)
        income = sum(
            float(tx["amount"]) for tx in in_range if tx["type"] == "income"
        )
        expense = sum(
            float(tx["amount"]) for tx in in_range if tx["type"] == "expense"
        )
        return income - expense

    @rx.var
    async def expense_by_category(self) -> list[dict]:
        ts = await self.get_state(TransactionState)
        totals: dict[str, float] = {}
        for tx in self._transactions_in_range(ts.transactions):
            if tx["type"] == "expense":
                name = tx["category"]["name"]
                totals[name] = totals.get(name, 0.0) + float(tx["amount"])
        top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
        fills = ["#10b981", "#f97316", "#3b82f6", "#f59e0b", "#8b5cf6"]
        return [
            {"name": name, "value": round(value), "fill": fills[i % len(fills)]}
            for i, (name, value) in enumerate(top)
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
        """Generates a PDF report from real transaction data."""
        try:
            ts = await self.get_state(TransactionState)
            in_range = self._transactions_in_range(ts.transactions)
            income = sum(
                float(tx["amount"]) for tx in in_range if tx["type"] == "income"
            )
            expense = sum(
                float(tx["amount"]) for tx in in_range if tx["type"] == "expense"
            )
            net = income - expense

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
            c.drawString(100, 680, f"Total Income: ₹{income:,.2f}")
            c.drawString(100, 660, f"Total Expenses: ₹{expense:,.2f}")
            c.drawString(100, 640, f"Net Profit: ₹{net:,.2f}")
            c.save()
            self.generated_file_url = f"/_upload/{filename}"
            return rx.download(url=self.generated_file_url, filename=filename)
        except Exception as e:
            logging.exception(f"Error generating PDF: {e}")
            return rx.toast.error(f"Error generating PDF: {str(e)}")

    @rx.event
    async def generate_excel_report(self):
        """Generates an Excel report from real transaction data."""
        try:
            ts = await self.get_state(TransactionState)
            in_range = self._transactions_in_range(ts.transactions)
            income = sum(
                float(tx["amount"]) for tx in in_range if tx["type"] == "income"
            )
            expense = sum(
                float(tx["amount"]) for tx in in_range if tx["type"] == "expense"
            )
            net = income - expense

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
            ws.append(["Total Income", income])
            ws.append(["Total Expenses", expense])
            ws.append(["Net Profit", net])
            wb.save(file_path)
            self.generated_file_url = f"/_upload/{filename}"
            return rx.download(url=self.generated_file_url, filename=filename)
        except Exception as e:
            logging.exception(f"Error generating Excel: {e}")
            return rx.toast.error(f"Error generating Excel: {str(e)}")
