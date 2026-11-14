import importlib.util
import sys
import types
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_module(relative, stubs=None, name="tested_module"):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, stubs or {}):
        spec.loader.exec_module(module)
    return module


def settings_stubs():
    settings = types.ModuleType("openplotterSettings")
    for name in ("conf", "platform", "language"):
        setattr(settings, name, types.SimpleNamespace())
    return {"openplotterSettings": settings, "ujson": json}


class CANDetectionTest(unittest.TestCase):
    def test_renamed_can_is_detected_and_ethernet_is_not(self):
        stubs = settings_stubs()
        stubs["openplotterSettings"].language.Language = mock.Mock()
        module = load_module("openplotterCan/startup.py", stubs)
        module._ = lambda text: text
        interfaces = [
            {"ifname": "nmea0", "link_type": "can"},
            {"ifname": "can-monitor", "link_type": "ether"},
            {"ifname": "can0", "link_type": "can"},
        ]
        with mock.patch.object(
            module.subprocess,
            "check_output",
            return_value=json.dumps(interfaces).encode(),
        ):
            checker = module.Check(mock.Mock(), "en")
        self.assertEqual(checker.canList, ["nmea0", "can0"])


if __name__ == "__main__":
    unittest.main()
