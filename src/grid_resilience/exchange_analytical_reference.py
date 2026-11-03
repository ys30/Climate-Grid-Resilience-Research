"""Analytical reference for a single dispatchable supply technology.

For fixed hourly net interchange, nonnegative local generation cost, positive
spillage penalty and very high unserved-energy penalty, the merit-order
solution has a closed form. Used only as a synthetic test oracle.
"""
import numpy as np

def reference(demand_mw, interchange_mw, local_capacity_mw):
    demand=np.asarray(demand_mw,dtype=float)
    exchange=np.asarray(interchange_mw,dtype=float)
    if demand.ndim!=1 or demand.shape!=exchange.shape or demand.size==0:
        raise ValueError("Expected nonempty equal-length hourly vectors")
    if not np.isfinite(demand).all() or not np.isfinite(exchange).all():
        raise ValueError("Nonfinite reference inputs")
    if (demand<0).any() or not np.isfinite(local_capacity_mw) or local_capacity_mw<0:
        raise ValueError("Invalid local demand or capacity")
    imports=np.maximum(-exchange,0)
    exports=np.maximum(exchange,0)
    required=demand+exports-imports
    local=np.clip(required,0,local_capacity_mw)
    shortage=np.maximum(required-local,0)
    spilled=np.maximum(-required,0)
    return {
        "local_generation_mwh":float(local.sum()),
        "scheduled_import_mwh":float(imports.sum()),
        "scheduled_export_mwh":float(exports.sum()),
        "local_demand_mwh":float(demand.sum()),
        "unserved_mwh":float(shortage.sum()),
        "spilled_mwh":float(spilled.sum()),
        "hours_with_unserved":int((shortage>1e-6).sum()),
        "hours_with_spillage":int((spilled>1e-6).sum())
    }
