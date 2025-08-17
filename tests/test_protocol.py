"""Test protocol communication functionality."""

from unittest.mock import MagicMock, patch

import pytest

from mhz14a.exceptions import MHZ14AError
from mhz14a.sensor import MHZ14A


class TestMHZ14AProtocol:
    """Test MH-Z14A protocol communication."""

    def test_read_co2_success(self):
        """Test successful CO₂ reading."""
        # Mock response for 2000 ppm: FF 86 07 D0 00 00 00 00 A7
        mock_response = bytes([0xFF, 0x86, 0x07, 0xD0, 0x00, 0x00, 0x00, 0x00, 0xA7])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            ppm = sensor.read_co2()
            assert ppm == 2000  # 0x07 * 256 + 0xD0 = 2000
            
            # Verify command was sent correctly
            expected_command = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
            mock_instance.write.assert_called_with(expected_command)

    def test_read_co2_415_ppm(self):
        """Test CO₂ reading for typical outdoor air (415 ppm)."""
        # Mock response for 415 ppm: FF 86 01 9F 00 00 00 00 BD
        mock_response = bytes([0xFF, 0x86, 0x01, 0x9F, 0x00, 0x00, 0x00, 0x00, 0xBD])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            ppm = sensor.read_co2()
            assert ppm == 415  # 0x01 * 256 + 0x9F = 415

    def test_invalid_header_error(self):
        """Test error handling for invalid response header."""
        # Response with invalid header (0xFE instead of 0xFF)
        mock_response = bytes([0xFE, 0x86, 0x07, 0xD0, 0x00, 0x00, 0x00, 0x00, 0xA8])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            with pytest.raises(MHZ14AError, match="Invalid header"):
                sensor.read_co2()

    def test_checksum_error(self):
        """Test error handling for checksum mismatch."""
        # Response with invalid checksum (0xA6 instead of 0xA7)
        mock_response = bytes([0xFF, 0x86, 0x07, 0xD0, 0x00, 0x00, 0x00, 0x00, 0xA6])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            with pytest.raises(MHZ14AError, match="Checksum mismatch"):
                sensor.read_co2()

    def test_timeout_error(self):
        """Test timeout error handling."""
        import serial
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.side_effect = serial.SerialTimeoutException("Timeout")
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            with pytest.raises(MHZ14AError, match="Read failed after 3 attempts"):
                sensor.read_co2()

    def test_partial_write_error(self):
        """Test partial write error handling."""
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 5  # Partial write (5 instead of 9 bytes)
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            with pytest.raises(MHZ14AError, match="Partial write"):
                sensor.read_co2()

    def test_incomplete_response_error(self):
        """Test incomplete response error handling."""
        # Response with only 7 bytes instead of 9
        mock_response = bytes([0xFF, 0x86, 0x07, 0xD0, 0x00, 0x00, 0x00])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            with pytest.raises(MHZ14AError, match="Incomplete response"):
                sensor.read_co2()

    def test_zero_calibrate_success(self):
        """Test successful zero calibration."""
        # Mock response for zero calibration: FF 87 01 00 00 00 00 00 77
        mock_response = bytes([0xFF, 0x87, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            # Should not raise an exception
            sensor.zero_calibrate()
            
            # Verify command was sent correctly
            expected_command = bytes([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78])
            mock_instance.write.assert_called_with(expected_command)

    def test_span_calibrate_success(self):
        """Test successful span calibration."""
        # Mock response for span calibration: FF 88 01 00 00 00 00 00 76
        mock_response = bytes([0xFF, 0x88, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x76])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            # Should not raise an exception
            sensor.span_calibrate(2000)
            
            # Verify command was sent correctly (2000 = 0x07D0)
            expected_command = bytes([0xFF, 0x01, 0x88, 0x07, 0xD0, 0x00, 0x00, 0x00, 0x70])
            mock_instance.write.assert_called_with(expected_command)

    def test_set_abc_enable(self):
        """Test enabling ABC."""
        # Mock response for ABC enable: FF 79 01 00 00 00 00 00 85
        mock_response = bytes([0xFF, 0x79, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x85])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            # Should not raise an exception
            sensor.set_abc(True)
            
            # Verify command was sent correctly (enable ABC = 0xA0)
            expected_command = bytes([0xFF, 0x01, 0x79, 0xA0, 0x00, 0x00, 0x00, 0x00, 0xE6])
            mock_instance.write.assert_called_with(expected_command)

    def test_set_range_5000(self):
        """Test setting range to 5000 ppm."""
        # Mock response for range setting: FF 99 01 00 00 00 00 00 65
        mock_response = bytes([0xFF, 0x99, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x65])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            sensor = MHZ14A('/dev/test')
            sensor._connect()
            
            # Should not raise an exception
            sensor.set_range(5000)
            
            # Verify command was sent correctly (5000 = 0x1388)
            expected_command = bytes([0xFF, 0x01, 0x99, 0x13, 0x88, 0x00, 0x00, 0x00, 0x55])
            mock_instance.write.assert_called_with(expected_command)

    def test_invalid_range_error(self):
        """Test error for invalid range value."""
        sensor = MHZ14A('/dev/test')
        
        with pytest.raises(ValueError, match="Invalid range"):
            sensor.set_range(3000)  # Invalid range

    def test_context_manager(self):
        """Test context manager functionality."""
        mock_response = bytes([0xFF, 0x86, 0x01, 0x9F, 0x00, 0x00, 0x00, 0x00, 0xBD])
        
        with patch('serial.Serial') as mock_serial:
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            mock_instance.write.return_value = 9
            mock_instance.read.return_value = mock_response
            
            with MHZ14A('/dev/test') as sensor:
                ppm = sensor.read_co2()
                assert ppm == 415
                
            # Verify connection was closed
            mock_instance.close.assert_called_once()
