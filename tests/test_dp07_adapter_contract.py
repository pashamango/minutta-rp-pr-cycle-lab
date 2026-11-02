import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _adapters():
    entries = json.loads((ROOT / "docs/capability-registry.json").read_text())["capabilities"]
    return {e["id"]: e for e in entries if e.get("kind") == "provider_adapter"}


def test_provider_adapters_have_permission_and_provenance_contracts():
    adapters = _adapters()
    assert {"adapter.linear", "adapter.figma", "adapter.sales"} <= adapters.keys()
    for entry in adapters.values():
        for field in ("permission_probe", "source_identity", "cursor_contract", "resource_contract", "rate_budget_contract", "revocation_test"):
            assert entry[field]
        assert entry["access_state"] == "READ_BLOCKED"


def test_sales_never_invents_plugin_activity():
    sales = _adapters()["adapter.sales"]
    assert "none" in sales["documented_api"].lower()
    assert "zero activity" in sales["policy"].lower()
    assert sales["source_of_truth"] == "not_available"
