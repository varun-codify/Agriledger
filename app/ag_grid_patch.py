"""Force AG Grid to run in Community-only mode.

reflex_ag_grid ships with `ag-grid-enterprise` imported unconditionally and
calls `LicenseManager.setLicenseKey(null)`. Without a paid enterprise license
the grid then renders a persistent "For Trial Use Only" watermark.

All grids in this app pass `enable_enterprise_modules=False` and only use
Community features (sorting, filters, pagination), so we strip the enterprise
import and the license-manager call entirely. This removes the watermark.
"""

from reflex_ag_grid.ag_grid import AgGrid

_AG_GRID_ENTERPRISE = "ag-grid-enterprise"

_orig_add_imports = AgGrid.add_imports
_orig_add_custom_code = AgGrid.add_custom_code


def _community_only_add_imports(self):
    """Drop ag-grid-enterprise from the generated JS imports."""
    imports = _orig_add_imports(self)
    cleaned = {}
    for module, names in imports.items():
        if module == _AG_GRID_ENTERPRISE:
            continue
        if module == "":
            names = [n for n in names if n != _AG_GRID_ENTERPRISE]
        cleaned[module] = names
    return cleaned


def _noop_add_custom_code(self) -> list[str]:
    """Skip the LicenseManager.setLicenseKey call (enterprise is gone)."""
    return []


AgGrid.add_imports = _community_only_add_imports
AgGrid.add_custom_code = _noop_add_custom_code
