"""Tests for Denkovi JSON parsing."""

from custom_components.denkovi-smartden-ip.api import DenkoviClient


def test_parse_ip16r_relays():
    data = [{"Name": f"RELAY{i}", "Value": str(i % 2)} for i in range(1, 17)]
    result = DenkoviClient._parse_named_values(data, "RELAY", 16, binary=True)
    assert len(result) == 16
    assert result[1] is True
    assert result[2] is False


def test_parse_ip32in_digital_inputs():
    data = [{"Name": f"DIn{i}", "Value": str(i % 2)} for i in range(1, 17)]
    result = DenkoviClient._parse_named_values(data, "DIn", 16, binary=True)
    assert len(result) == 16
    assert result[3] is True


def test_parse_analog_measurements():
    data = [
        {"Name": f"AI{i}", "Value": str(i * 10), "Measure": f"{i}.0 Volt"}
        for i in range(1, 9)
    ]
    result = DenkoviClient._parse_measurements(data, "AI", 8)
    assert result[3]["value"] == 30
    assert result[3]["measure"] == "3.0 Volt"


def test_parse_unavailable_temperature():
    data = [
        {"Name": f"TI{i}", "Value": "---"}
        for i in range(1, 9)
    ]
    result = DenkoviClient._parse_measurements(data, "TI", 8)
    assert result[1]["value"] is None
