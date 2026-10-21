import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class MQTTDiscoveryTests(unittest.TestCase):
    def setUp(self):
        source_path = Path(__file__).resolve().parents[1] / "python" / "getjudo.py"
        source = ast.parse(source_path.read_text(encoding="utf-8"))
        # Load only definitions: importing getjudo starts cloud requests and timers.
        definitions = ast.Module(
            body=[
                node for node in source.body
                if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                and node.name in {
                    "entity", "notification_entity", "publish_json", "on_connect"
                }
            ],
            type_ignores=[],
        )
        self.client = Mock()
        self.namespace = {
            "json": json,
            "client": self.client,
            "client_id": "Judo-test",
            "availability_topic": "test/Judo/status",
            "state_topic": "test/Judo/state",
            "command_topic": "test/Judo/command",
            "notification_topic": "test/Judo/notify",
            "config_getjudo": SimpleNamespace(
                MANUFACTURER="test",
                NAME="Judo",
                LOCATION="test",
                SW_VERSION="2.0",
                AVAILABILITY_ONLINE="online",
                AVAILABILITY_OFFLINE="offline",
            ),
            "messages_getjudo": SimpleNamespace(debug=["debug"] * 27),
        }
        exec(compile(definitions, str(source_path), "exec"), self.namespace)

    def test_total_increasing_discovery_is_repeatable(self):
        for name in (
            "Gesamtwasserverbrauch",
            "Gesamthartwasseranteil",
            "Gesamtweichwasseranteil",
        ):
            with self.subTest(name=name):
                sensor = self.namespace["entity"](
                    name, "mdi:water", "total_increasing", "m\u00b3"
                )
                self.client.reset_mock()
                for _ in range(3):
                    sensor.send_entity_autoconfig()
                calls = self.client.publish.call_args_list
                self.assertEqual(len(calls), 3)
                self.assertEqual(calls[0], calls[1])
                self.assertEqual(calls[0], calls[2])
                topic, payload = calls[-1].args
                self.assertEqual(
                    topic, f"homeassistant/sensor/test/Judo_{name}/config"
                )
                config = json.loads(payload)
                self.assertEqual(config["state_class"], "total_increasing")
                self.assertEqual(config["device_class"], "water")
                self.assertEqual(config["unit_of_measurement"], "m\u00b3")
                self.assertEqual(config["unique_id"], f"Judo-test_{name}")
                self.assertEqual(config["state_topic"], "test/Judo/state")
                self.assertEqual(calls[-1].kwargs, {"qos": 0, "retain": True})
                self.assertEqual(sensor.entity_type, "total_increasing")

    def test_reconnect_preserves_water_sensor_discovery(self):
        sensor = self.namespace["entity"](
            "Gesamtwasserverbrauch", "mdi:water", "total_increasing", "m\u00b3"
        )
        self.namespace["gc"] = SimpleNamespace(get_objects=lambda: [sensor])
        self.namespace["notify"] = self.namespace["notification_entity"](
            "Meldung", "mdi:alert-outline"
        )
        on_connect = self.namespace["on_connect"]
        on_connect(self.client, None, {}, 0)
        first_connection = self.client.publish.call_args_list[:]
        self.client.reset_mock()
        on_connect(self.client, None, {}, 0)
        self.assertEqual(
            self.client.publish.call_args_list, first_connection
        )
        self.client.subscribe.assert_called_once_with("test/Judo/command")

    def test_other_discovery_types_are_unchanged(self):
        for entity_type in ("sensor", "number", "switch", "select"):
            with self.subTest(entity_type=entity_type):
                unit = ["off", "on"] if entity_type == "select" else "L"
                sensor = self.namespace["entity"](
                    "test", "mdi:water", entity_type, unit
                )
                sensor.send_entity_autoconfig()
                topic, payload = self.client.publish.call_args.args
                self.assertEqual(
                    topic, f"homeassistant/{entity_type}/test/Judo_test/config"
                )
                config = json.loads(payload)
                self.assertNotIn("state_class", config)
                self.assertEqual(sensor.entity_type, entity_type)
                if entity_type in ("number", "switch", "select"):
                    self.assertEqual(
                        config["command_topic"], "test/Judo/command"
                    )
                if entity_type in ("sensor", "number"):
                    self.assertEqual(config["unit_of_measurement"], unit)
                if entity_type == "number":
                    self.assertEqual(
                        (config["min"], config["max"], config["step"]),
                        (1, 100, 1),
                    )
                elif entity_type == "switch":
                    self.assertEqual(config["payload_on"], '{"test": 1}')
                    self.assertEqual(config["payload_off"], '{"test": 0}')
                elif entity_type == "select":
                    self.assertEqual(config["options"], unit)


if __name__ == "__main__":
    unittest.main()
