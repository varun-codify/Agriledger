"""AG Grid table for cattle management with sorting, filtering, and CSV export."""

import reflex as rx

try:
    import reflex_ag_grid as rx_ag

    HAS_AG_GRID = True
except ImportError:
    HAS_AG_GRID = False

from app.states.cattle_state import CattleState


CATTLE_COLUMN_DEFS = [
    {
        "headerName": "Name",
        "field": "name",
        "sortable": True,
        "filter": True,
        "cellRenderer": "agGroupCellRenderer",
        "width": 140,
    },
    {
        "headerName": "Tag",
        "field": "tag_number",
        "sortable": True,
        "filter": True,
        "width": 90,
    },
    {
        "headerName": "Type",
        "field": "animal_type",
        "sortable": True,
        "filter": True,
        "width": 100,
    },
    {
        "headerName": "Breed",
        "field": "breed",
        "sortable": True,
        "filter": True,
        "width": 110,
    },
    {
        "headerName": "Age",
        "field": "age",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "width": 70,
    },
    {
        "headerName": "Weight (kg)",
        "field": "weight",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"textAlign": "right"},
        "width": 110,
    },
    {
        "headerName": "Health",
        "field": "health_status",
        "sortable": True,
        "filter": True,
        "width": 120,
    },
    {
        "headerName": "Purchase Price",
        "field": "purchase_price",
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "cellStyle": {"textAlign": "right"},
        "valueFormatter": "'₹' + value",
        "width": 130,
    },
    {
        "headerName": "Active",
        "field": "is_active",
        "sortable": True,
        "filter": True,
        "width": 80,
        "cellStyle": {"textAlign": "center"},
    },
]


def cattle_grid(row_data=None) -> rx.Component:
    """AG Grid displaying cattle with advanced features.

    Args:
        row_data: Optional data source; defaults to the full cattle list.
    """
    if not HAS_AG_GRID:
        return rx.el.div(
            rx.el.p("AG Grid not available. Install with: pip install reflex-ag-grid"),
            class_name="text-stone-500 text-sm p-4",
        )

    data = CattleState.cattle_list if row_data is None else row_data
    return rx.el.div(
        rx.el.h3(
            "All Animals (Table View)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx_ag.ag_grid(
            id="cattle-grid",
            column_defs=CATTLE_COLUMN_DEFS,
            row_data=data,
            row_selection="single",
            pagination=True,
            pagination_page_size=20,
            enable_enterprise_modules=False,
            dom_layout="autoHeight",
            suppress_row_hover_highlight=False,
            animate_rows=True,
            class_name="ag-theme-alpine",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )
