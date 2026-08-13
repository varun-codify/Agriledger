"""AG Grid table for breeding cycles with sorting, filtering, and export."""

import reflex as rx

try:
    import reflex_ag_grid as rx_ag

    HAS_AG_GRID = True
except ImportError:
    HAS_AG_GRID = False

from app.states.breeding_state import BreedingState


BREEDING_COLUMN_DEFS = [
    {
        "headerName": "Animal",
        "field": "cattle_name",
        "sortable": True,
        "filter": True,
        "width": 130,
    },
    {
        "headerName": "Type",
        "field": "cattle_type",
        "sortable": True,
        "filter": True,
        "width": 100,
    },
    {
        "headerName": "Insemination Date",
        "field": "insemination_date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "width": 150,
    },
    {
        "headerName": "Status",
        "field": "status",
        "sortable": True,
        "filter": True,
        "width": 140,
        "cellStyle": {"fontWeight": "bold"},
    },
    {
        "headerName": "Pregnancy Confirmed",
        "field": "pregnancy_confirmed",
        "sortable": True,
        "filter": True,
        "width": 160,
        "cellStyle": {"textAlign": "center"},
    },
    {
        "headerName": "Confirmation Date",
        "field": "pregnancy_confirmation_date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "width": 160,
    },
    {
        "headerName": "Expected Calving",
        "field": "expected_calving_date",
        "sortable": True,
        "filter": "agDateColumnFilter",
        "width": 150,
    },
    {
        "headerName": "Calf Born",
        "field": "calf_born",
        "sortable": True,
        "filter": True,
        "width": 100,
        "cellStyle": {"textAlign": "center"},
    },
    {
        "headerName": "Calf Sex",
        "field": "calf_sex",
        "sortable": True,
        "filter": True,
        "width": 100,
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


def breeding_grid(row_data=None) -> rx.Component:
    """AG Grid displaying breeding cycles.

    Args:
        row_data: Optional data source; defaults to the full cycle list.
    """
    if not HAS_AG_GRID:
        return rx.el.div(
            rx.el.p("AG Grid not available. Install with: pip install reflex-ag-grid"),
            class_name="text-stone-500 text-sm p-4",
        )

    data = BreedingState.breeding_cycles if row_data is None else row_data
    return rx.el.div(
        rx.el.h3(
            "All Breeding Cycles (Table View)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx_ag.ag_grid(
            id="breeding-grid",
            column_defs=BREEDING_COLUMN_DEFS,
            row_data=data,
            row_selection="single",
            pagination=True,
            pagination_page_size=15,
            enable_enterprise_modules=False,
            dom_layout="autoHeight",
            suppress_row_hover_highlight=False,
            animate_rows=True,
            class_name="ag-theme-alpine",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )
