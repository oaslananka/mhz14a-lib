"""Test checksum calculation functionality."""

from mhz14a.sensor import _checksum


def test_checksum_read_co2_command():
    """Test checksum calculation for read CO₂ command."""
    # Command: FF 01 86 00 00 00 00 00
    frame = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00])
    expected_checksum = 0x79  # 121 decimal
    assert _checksum(frame) == expected_checksum


def test_checksum_various_commands():
    """Test checksum calculation for various commands."""
    test_cases = [
        # Zero calibration: FF 01 87 00 00 00 00 00
        (bytes([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00]), 0x78),
        # Span calibration 2000ppm: FF 01 88 07 D0 00 00 00
        (bytes([0xFF, 0x01, 0x88, 0x07, 0xD0, 0x00, 0x00, 0x00]), 0x70),
        # ABC enable: FF 01 79 A0 00 00 00 00
        (bytes([0xFF, 0x01, 0x79, 0xA0, 0x00, 0x00, 0x00, 0x00]), 0xE6),
        # Range 5000: FF 01 99 13 88 00 00 00
        (bytes([0xFF, 0x01, 0x99, 0x13, 0x88, 0x00, 0x00, 0x00]), 0x55),
    ]
    
    for frame, expected in test_cases:
        assert _checksum(frame) == expected


def test_checksum_response_validation():
    """Test checksum validation for sensor responses."""
    # Typical response for 2000 ppm: FF 86 07 D0 00 00 00 00 A7
    response = bytes([0xFF, 0x86, 0x07, 0xD0, 0x00, 0x00, 0x00, 0x00])
    expected_checksum = 0xA7
    assert _checksum(response) == expected_checksum
    
    # Response for 415 ppm: FF 86 01 9F 00 00 00 00 BD
    response = bytes([0xFF, 0x86, 0x01, 0x9F, 0x00, 0x00, 0x00, 0x00])
    expected_checksum = 0xBD
    assert _checksum(response) == expected_checksum


def test_checksum_edge_cases():
    """Test checksum calculation edge cases."""
    # All zeros except header and command
    frame = bytes([0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    assert _checksum(frame) == 0xFE
    
    # All 0xFF values
    frame = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    assert _checksum(frame) == 0x04  # (0xFF - (6 * 0xFF) + 1) & 0xFF
