"""AG Grid table for transactions with sorting, filtering, and CSV export."""

import reflex as rx

try:
    import reflex_ag_grid as rx_ag

    HAS_AG_GRID = True
except ImportError:
    HAS_AG_GRID = False

from app.states.transaction_state import TransactionState


TRANSACTION_COLUMN_DEFS = [
    {
        "headerName": "Date",
        "field": "date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "resizable": True,
        "width": 130,
    },
    {
        "headerName": "Type",
        "field": "type",
        "sortable": True,
        "filter": True,
        "cellStyle": {"fontWeight": "bold"},
        "width": 100,
    },
    {
        "headerName": "Category",
        "field": "category_name",
        "sortable": True,
        "filter": True,
        "width": 160,
    },
    {
        "headerName": "Amount",
        "field": "amount",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"fontWeight": "bold", "textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 120,
    },
    {
        "headerName": "Notes",
        "field": "notes",
        "sortable": False,
        "filter": True,
        "flex": 1,
        "minWidth": 150,
    },
]


MILK_SALE_COLUMN_DEFS = [
    {
        "headerName": "Date",
        "field": "date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "width": 120,
    },
    {
        "headerName": "Liters",
        "field": "liters",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "width": 90,
    },
    {
        "headerName": "Fat %",
        "field": "fat_percentage",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "width": 80,
    },
    {
        "headerName": "SNF %",
        "field": "snf_percentage",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "width": 80,
    },
    {
        "headerName": "Rate/L",
        "field": "rate_per_liter",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 90,
    },
    {
        "headerName": "Total",
        "field": "total_price",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"fontWeight": "bold", "textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 110,
    },
    {
        "headerName": "Buyer",
        "field": "buyer",
        "sortable": True,
        "filter": True,
        "flex": 1,
    },
]

COCONUT_SALE_COLUMN_DEFS = [
    {
        "headerName": "Date",
        "field": "date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "width": 120,
    },
    {
        "headerName": "Count",
        "field": "coconut_count",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "width": 90,
    },
    {
        "headerName": "Price/Each",
        "field": "price_per_coconut",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 110,
    },
    {
        "headerName": "Total",
        "field": "total_amount",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"fontWeight": "bold", "textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 110,
    },
    {
        "headerName": "Buyer",
        "field": "buyer",
        "sortable": True,
        "filter": True,
        "flex": 1,
    },
]


def _ag_grid_theme() -> dict:
    return {
        "header": {
            "background": "#f5f5f4",
            "color": "#44403c",
            "fontWeight": "bold",
        },
        "row": {
            "hover": "#f0fdf4",
        },
    }


def transactions_grid() -> rx.Component:
    """AG Grid displaying all transactions."""
    if not HAS_AG_GRID:
        return rx.el.div(
            rx.el.p("AG Grid not available. Install with: pip install reflex-ag-grid"),
            class_name="text-stone-500 text-sm p-4",
        )

    return rx.el.div(
        rx.el.h3(
            "All Transactions",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx_ag.ag_grid(
            id="transactions-grid",
            column_defs=TRANSACTION_COLUMN_DEFS,
            row_data=TransactionState.transactions_grid_data,
            row_selection="single",
            pagination=True,
            pagination_page_size=20,
            enable_enterprise_modules=False,
            dom_layout="autoHeight",
            suppress_row_hover_highlight=False,
            animate_rows=True,
            class_name="ag-theme-alpine",
            width="100%",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def milk_sales_grid() -> rx.Component:
    """AG Grid displaying milk sales with quality metrics."""
    if not HAS_AG_GRID:
        return rx.el.div(
            rx.el.p("AG Grid not available."),
            class_name="text-stone-500 text-sm p-4",
        )

    return rx.el.div(
        rx.el.h3(
            "Milk Sales",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx_ag.ag_grid(
            id="milk-sales-grid",
            column_defs=MILK_SALE_COLUMN_DEFS,
            row_data=TransactionState.milk_sales,
            row_selection="single",
            pagination=True,
            pagination_page_size=15,
            enable_enterprise_modules=False,
            dom_layout="autoHeight",
            animate_rows=True,
            class_name="ag-theme-alpine",
            width="100%",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def coconut_sales_grid() -> rx.Component:
    """AG Grid displaying coconut sales."""
    if not HAS_AG_GRID:
        return rx.el.div(
            rx.el.p("AG Grid not available."),
            class_name="text-stone-500 text-sm p-4",
        )

    return rx.el.div(
        rx.el.h3(
            "Coconut Sales",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx_ag.ag_grid(
            id="coconut-sales-grid",
            column_defs=COCONUT_SALE_COLUMN_DEFS,
            row_data=TransactionState.coconut_sales,
            row_selection="single",
            pagination=True,
            pagination_page_size=15,
            enable_enterprise_modules=False,
            dom_layout="autoHeight",
            animate_rows=True,
            class_name="ag-theme-alpine",
            width="100%",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def transactions_page() -> rx.Component:
    """Full page with all transaction grids, switchable via tabs."""
    from app.components.common import segmented_control
    from app.components.layout import dashboard_layout

    return dashboard_layout(
        rx.el.div(
            rx.el.div(
                segmented_control(
                    TransactionState.active_table_tab,
                    [
                        ("all", "All Transactions", "list"),
                        ("milk", "Milk Sales", "droplets"),
                        ("coconut", "Coconut Sales", "tree-palm"),
                    ],
                    TransactionState.set_active_table_tab,
                    container_class="flex-wrap",
                ),
                rx.el.a(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Transaction",
                    href="/add-transaction",
                    class_name="flex items-center bg-emerald-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-emerald-600 transition-all",
                ),
                class_name="flex items-center justify-between mb-6 flex-wrap gap-4",
            ),
            rx.cond(
                TransactionState.active_table_tab == "all",
                transactions_grid(),
                rx.cond(
                    TransactionState.active_table_tab == "milk",
                    milk_sales_grid(),
                    coconut_sales_grid(),
                ),
            ),
            class_name="max-w-7xl mx-auto",
        ),
        "Transactions",
    )
