import ast
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("firmware,expected", [(0, "0"), (102, "102"), ("1.0.2", "1.0.2"), ("", ""), (None, None)])
def test_device_info_preserves_identity_and_normalizes_firmware(firmware, expected):
    source = Path(__file__).parents[1] / "custom_components/linkedgo_bridge/climate.py"
    getter = next(node for node in ast.walk(ast.parse(source.read_text()))
                  if isinstance(node, ast.FunctionDef) and node.name == "device_info")
    getter.decorator_list = []
    namespace = {"DeviceInfo": dict, "DOMAIN": "linkedgo_bridge"}
    exec(compile(ast.Module(body=[getter], type_ignores=[]), str(source), "exec"), namespace)
    device = SimpleNamespace(device_id="device-1", device_name="Bedroom", sw_version=firmware, product_model="ST830")
    entity = SimpleNamespace(entity=device, hub=SimpleNamespace(manufacturer="LinkedGo"))
    assert namespace["device_info"](entity) == {
        "identifiers": {("linkedgo_bridge", "device-1")},
        "name": "Bedroom",
        "sw_version": expected,
        "model": "ST830",
        "manufacturer": "LinkedGo",
    }
