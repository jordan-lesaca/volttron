# -*- coding: utf-8 -*-
"""
Mock tests for Home Assistant driver interface.
These tests don't require an actual Home Assistant instance.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import json
import os

# Add the platform_driver directory to the path so we can import the interface
# Get the parent directory (PlatformDriverAgent)
test_dir = os.path.dirname(os.path.abspath(__file__))
platform_driver_agent_dir = os.path.dirname(test_dir)
platform_driver_dir = os.path.join(platform_driver_agent_dir, 'platform_driver')
interfaces_dir = os.path.join(platform_driver_dir, 'interfaces')

# Add to sys.path
if interfaces_dir not in sys.path:
    sys.path.insert(0, interfaces_dir)

# Mock the volttron imports before importing the interface
sys.modules['volttron'] = MagicMock()
sys.modules['volttron.platform'] = MagicMock()
sys.modules['volttron.platform.agent'] = MagicMock()
sys.modules['volttron.platform.agent.utils'] = MagicMock()
sys.modules['volttron.platform.vip'] = MagicMock()
sys.modules['volttron.platform.vip.agent'] = MagicMock()

# Create proper mock for platform_driver module
platform_driver_mock = MagicMock()
sys.modules['platform_driver'] = platform_driver_mock

# Create the interfaces submodule properly
interfaces_mock = MagicMock()
sys.modules['platform_driver.interfaces'] = interfaces_mock

# Mock base classes with proper attribute initialization
class BaseRegister:
    """Mock BaseRegister that properly stores attributes"""
    def __init__(self, register_type, read_only, pointName, units, description=''):
        self.register_type = register_type
        self.read_only = read_only
        self.point_name = pointName
        self.units = units
        self.description = description

BaseInterface = type('BaseInterface', (), {})
BasicRevert = type('BasicRevert', (), {})

# Attach the base classes to the mock
interfaces_mock.BaseInterface = BaseInterface
interfaces_mock.BaseRegister = BaseRegister
interfaces_mock.BasicRevert = BasicRevert


class MockResponse:
    """Mock HTTP response object"""
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data


@pytest.fixture
def mock_interface():
    """Create a mock Home Assistant interface"""
    from home_assistant import Interface
    
    interface = Interface()
    interface.ip_address = "192.168.1.100"
    interface.access_token = "test_token"
    interface.port = "8123"
    return interface


@pytest.fixture
def sample_registry_config():
    """Sample registry configuration for testing"""
    return [
        {
            "Entity ID": "light.living_room",
            "Entity Point": "state",
            "Volttron Point Name": "light_state",
            "Units": "On/Off",
            "Writable": True,
            "Type": "int",
            "Notes": "Living room light"
        },
        {
            "Entity ID": "light.living_room",
            "Entity Point": "brightness",
            "Volttron Point Name": "light_brightness",
            "Units": "brightness",
            "Writable": True,
            "Type": "int",
            "Notes": "Living room light brightness"
        },
        {
            "Entity ID": "switch.outlet",
            "Entity Point": "state",
            "Volttron Point Name": "switch_state",
            "Units": "On/Off",
            "Writable": True,
            "Type": "int",
            "Notes": "Outlet switch"
        },
        {
            "Entity ID": "fan.bedroom",
            "Entity Point": "state",
            "Volttron Point Name": "fan_state",
            "Units": "On/Off",
            "Writable": True,
            "Type": "int",
            "Notes": "Bedroom fan"
        },
        {
            "Entity ID": "climate.thermostat",
            "Entity Point": "state",
            "Volttron Point Name": "thermostat_mode",
            "Units": "mode",
            "Writable": True,
            "Type": "int",
            "Notes": "Thermostat mode"
        },
        {
            "Entity ID": "climate.thermostat",
            "Entity Point": "temperature",
            "Volttron Point Name": "thermostat_temp",
            "Units": "F",
            "Writable": True,
            "Type": "float",
            "Notes": "Thermostat temperature"
        }
    ]


class TestHomeAssistantConfiguration:
    """Test configuration and initialization"""
    
    def test_configure_with_valid_config(self, mock_interface, sample_registry_config):
        """Test that configuration works with valid parameters"""
        config_dict = {
            "ip_address": "192.168.1.100",
            "access_token": "test_token",
            "port": "8123"
        }
        
        mock_interface.parse_config = Mock()
        mock_interface.configure(config_dict, sample_registry_config)
        
        assert mock_interface.ip_address == "192.168.1.100"
        assert mock_interface.access_token == "test_token"
        assert mock_interface.port == "8123"
    
    def test_configure_missing_ip_address(self, mock_interface):
        """Test that missing IP address raises ValueError"""
        config_dict = {
            "access_token": "test_token",
            "port": "8123"
        }
        
        with pytest.raises(ValueError, match="IP address is required"):
            mock_interface.configure(config_dict, [])
    
    def test_configure_missing_access_token(self, mock_interface):
        """Test that missing access token raises ValueError"""
        config_dict = {
            "ip_address": "192.168.1.100",
            "port": "8123"
        }
        
        with pytest.raises(ValueError, match="Access token is required"):
            mock_interface.configure(config_dict, [])
    
    def test_configure_missing_port(self, mock_interface):
        """Test that missing port raises ValueError"""
        config_dict = {
            "ip_address": "192.168.1.100",
            "access_token": "test_token"
        }
        
        with pytest.raises(ValueError, match="Port is required"):
            mock_interface.configure(config_dict, [])


class TestLightControl:
    """Test light entity control"""
    
    @patch('home_assistant.requests.post')
    def test_turn_on_lights(self, mock_post, mock_interface):
        """Test turning on a light"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_on_lights("light.living_room")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "light/turn_on" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "light.living_room"
    
    @patch('home_assistant.requests.post')
    def test_turn_off_lights(self, mock_post, mock_interface):
        """Test turning off a light"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_off_lights("light.living_room")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "light/turn_off" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "light.living_room"
    
    @patch('home_assistant.requests.post')
    def test_change_brightness(self, mock_post, mock_interface):
        """Test changing light brightness"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.change_brightness("light.living_room", 128)
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['brightness'] == 128
    
    @patch('home_assistant.requests.post')
    def test_brightness_out_of_range_low(self, mock_post, mock_interface):
        """Test that brightness below 0 raises ValueError"""
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "light_brightness", "brightness", int, {},
            "light.living_room", "brightness"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        with pytest.raises(ValueError, match="Brightness value should be an integer between 0 and 255"):
            mock_interface._set_point("light_brightness", -1)
    
    @patch('home_assistant.requests.post')
    def test_brightness_out_of_range_high(self, mock_post, mock_interface):
        """Test that brightness above 255 raises ValueError"""
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "light_brightness", "brightness", int, {},
            "light.living_room", "brightness"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        with pytest.raises(ValueError, match="Brightness value should be an integer between 0 and 255"):
            mock_interface._set_point("light_brightness", 300)


class TestSwitchControl:
    """Test switch entity control"""
    
    @patch('home_assistant.requests.post')
    def test_turn_on_switch(self, mock_post, mock_interface):
        """Test turning on a switch"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_on_switch("switch.outlet")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "switch/turn_on" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "switch.outlet"
    
    @patch('home_assistant.requests.post')
    def test_turn_off_switch(self, mock_post, mock_interface):
        """Test turning off a switch"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_off_switch("switch.outlet")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "switch/turn_off" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "switch.outlet"
    
    @patch('home_assistant.requests.post')
    def test_set_switch_via_set_point(self, mock_post, mock_interface):
        """Test setting switch state via _set_point method"""
        mock_post.return_value = MockResponse({}, 200)
        
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        # Turn on
        mock_interface._set_point("switch_state", 1)
        assert mock_post.called
        assert "switch/turn_on" in mock_post.call_args[0][0]
        
        # Turn off
        mock_post.reset_mock()
        mock_interface._set_point("switch_state", 0)
        assert "switch/turn_off" in mock_post.call_args[0][0]
    
    def test_set_switch_invalid_value(self, mock_interface):
        """Test that invalid switch values raise ValueError"""
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        with pytest.raises(ValueError, match="must be 1 \\(on\\) or 0 \\(off\\)"):
            mock_interface._set_point("switch_state", 5)


class TestFanControl:
    """Test fan entity control"""
    
    @patch('home_assistant.requests.post')
    def test_turn_on_fan(self, mock_post, mock_interface):
        """Test turning on a fan"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_on_fan("fan.bedroom")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "fan/turn_on" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "fan.bedroom"
    
    @patch('home_assistant.requests.post')
    def test_turn_off_fan(self, mock_post, mock_interface):
        """Test turning off a fan"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.turn_off_fan("fan.bedroom")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "fan/turn_off" in call_args[0][0]
        assert call_args[1]['json']['entity_id'] == "fan.bedroom"
    
    @patch('home_assistant.requests.post')
    def test_set_fan_via_set_point(self, mock_post, mock_interface):
        """Test setting fan state via _set_point method"""
        mock_post.return_value = MockResponse({}, 200)
        
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "fan_state", "On/Off", int, {},
            "fan.bedroom", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        # Turn on
        mock_interface._set_point("fan_state", 1)
        assert "fan/turn_on" in mock_post.call_args[0][0]
        
        # Turn off
        mock_post.reset_mock()
        mock_interface._set_point("fan_state", 0)
        assert "fan/turn_off" in mock_post.call_args[0][0]


class TestThermostatControl:
    """Test thermostat/climate entity control"""
    
    @patch('home_assistant.requests.post')
    def test_change_thermostat_mode(self, mock_post, mock_interface):
        """Test changing thermostat mode"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface.change_thermostat_mode("climate.thermostat", "heat")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "climate/set_hvac_mode" in call_args[0][0]
        assert call_args[1]['json']['hvac_mode'] == "heat"
    
    @patch('home_assistant.requests.post')
    def test_set_thermostat_temperature_fahrenheit(self, mock_post, mock_interface):
        """Test setting thermostat temperature in Fahrenheit"""
        mock_post.return_value = MockResponse({}, 200)
        mock_interface.units = "F"
        
        mock_interface.set_thermostat_temperature("climate.thermostat", 72)
        
        call_args = mock_post.call_args
        assert call_args[1]['json']['temperature'] == 72
    
    @patch('home_assistant.requests.post')
    def test_set_thermostat_temperature_celsius(self, mock_post, mock_interface):
        """Test setting thermostat temperature with Celsius conversion"""
        mock_post.return_value = MockResponse({}, 200)
        mock_interface.units = "C"
        
        # 72°F should convert to 22.2°C
        mock_interface.set_thermostat_temperature("climate.thermostat", 72)
        
        call_args = mock_post.call_args
        # Check that temperature was converted (72F = 22.2C)
        assert call_args[1]['json']['temperature'] == pytest.approx(22.2, rel=0.1)
    
    @patch('home_assistant.requests.post')
    def test_set_thermostat_mode_via_set_point(self, mock_post, mock_interface):
        """Test setting thermostat mode via _set_point"""
        mock_post.return_value = MockResponse({}, 200)
        
        from home_assistant import HomeAssistantRegister
        register = HomeAssistantRegister(
            False, "thermostat_mode", "mode", int, {},
            "climate.thermostat", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        # Test different mode values
        mock_interface._set_point("thermostat_mode", 0)  # off
        assert mock_post.call_args[1]['json']['hvac_mode'] == "off"
        
        mock_interface._set_point("thermostat_mode", 2)  # heat
        assert mock_post.call_args[1]['json']['hvac_mode'] == "heat"
        
        mock_interface._set_point("thermostat_mode", 3)  # cool
        assert mock_post.call_args[1]['json']['hvac_mode'] == "cool"
        
        mock_interface._set_point("thermostat_mode", 4)  # auto
        assert mock_post.call_args[1]['json']['hvac_mode'] == "auto"


class TestGetEntityData:
    """Test reading entity data from Home Assistant"""
    
    @patch('home_assistant.requests.get')
    def test_get_entity_data_success(self, mock_get, mock_interface):
        """Test successful entity data retrieval"""
        mock_response_data = {
            "state": "on",
            "attributes": {
                "brightness": 128,
                "color_temp": 370
            }
        }
        mock_get.return_value = MockResponse(mock_response_data, 200)
        
        result = mock_interface.get_entity_data("light.living_room")
        
        assert result == mock_response_data
        assert result['state'] == "on"
        assert result['attributes']['brightness'] == 128
    
    @patch('home_assistant.requests.get')
    def test_get_entity_data_failure(self, mock_get, mock_interface):
        """Test entity data retrieval with error"""
        mock_get.return_value = MockResponse({"error": "Not found"}, 404)
        
        with pytest.raises(Exception, match="Request failed with status code 404"):
            mock_interface.get_entity_data("light.nonexistent")


class TestScrapeAll:
    """Test the _scrape_all method"""
    
    @patch('home_assistant.requests.get')
    def test_scrape_all_lights(self, mock_get, mock_interface):
        """Test scraping light entity states"""
        from home_assistant import HomeAssistantRegister
        
        # Create registers
        light_state_reg = HomeAssistantRegister(
            True, "light_state", "On/Off", int, {},
            "light.living_room", "state"
        )
        light_brightness_reg = HomeAssistantRegister(
            True, "light_brightness", "brightness", int, {},
            "light.living_room", "brightness"
        )
        
        mock_interface.get_registers_by_type = Mock(return_value=[
            light_state_reg, light_brightness_reg
        ])
        
        # Mock API response
        mock_get.return_value = MockResponse({
            "state": "on",
            "attributes": {"brightness": 200}
        }, 200)
        
        result = mock_interface._scrape_all()
        
        assert result["light_state"] == 1  # "on" -> 1
        assert result["light_brightness"] == 200
    
    @patch('home_assistant.requests.get')
    def test_scrape_all_thermostat(self, mock_get, mock_interface):
        """Test scraping thermostat entity states"""
        from home_assistant import HomeAssistantRegister
        
        thermo_state_reg = HomeAssistantRegister(
            True, "thermostat_mode", "mode", int, {},
            "climate.thermostat", "state"
        )
        thermo_temp_reg = HomeAssistantRegister(
            True, "thermostat_temp", "F", float, {},
            "climate.thermostat", "temperature"
        )
        
        mock_interface.get_registers_by_type = Mock(return_value=[
            thermo_state_reg, thermo_temp_reg
        ])
        
        # Mock API response
        mock_get.return_value = MockResponse({
            "state": "heat",
            "attributes": {"temperature": 72.0}
        }, 200)
        
        result = mock_interface._scrape_all()
        
        assert result["thermostat_mode"] == 2  # "heat" -> 2
        assert result["thermostat_temp"] == 72.0
    
    @patch('home_assistant.requests.get')
    def test_scrape_all_switch(self, mock_get, mock_interface):
        """Test scraping switch entity states"""
        from home_assistant import HomeAssistantRegister
        
        switch_reg = HomeAssistantRegister(
            True, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        
        mock_interface.get_registers_by_type = Mock(return_value=[switch_reg])
        
        # Mock API response - switch is off
        mock_get.return_value = MockResponse({
            "state": "off",
            "attributes": {}
        }, 200)
        
        result = mock_interface._scrape_all()
        
        assert result["switch_state"] == 0  # "off" -> 0
    
    @patch('home_assistant.requests.get')
    def test_scrape_all_fan(self, mock_get, mock_interface):
        """Test scraping fan entity states"""
        from home_assistant import HomeAssistantRegister
        
        fan_reg = HomeAssistantRegister(
            True, "fan_state", "On/Off", int, {},
            "fan.bedroom", "state"
        )
        
        mock_interface.get_registers_by_type = Mock(return_value=[fan_reg])
        
        # Mock API response - fan is on
        mock_get.return_value = MockResponse({
            "state": "on",
            "attributes": {}
        }, 200)
        
        result = mock_interface._scrape_all()
        
        assert result["fan_state"] == 1  # "on" -> 1


class TestReadOnlyProtection:
    """Test that read-only points cannot be written"""
    
    def test_write_to_readonly_point(self, mock_interface):
        """Test that writing to read-only point raises IOError"""
        from home_assistant import HomeAssistantRegister
        
        # Create a read-only register
        register = HomeAssistantRegister(
            True,  # read_only=True
            "light_state", "On/Off", int, {},
            "light.living_room", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=register)
        
        with pytest.raises(IOError, match="Trying to write to a point configured read only"):
            mock_interface._set_point("light_state", 1)


class TestErrorHandling:
    """Test error handling in various scenarios"""
    
    @patch('home_assistant.requests.post')
    def test_api_call_failure(self, mock_post, mock_interface):
        """Test handling of failed API calls"""
        mock_post.return_value = MockResponse({"error": "Service unavailable"}, 503)
        
        with pytest.raises(Exception, match="Failed to"):
            mock_interface.turn_on_lights("light.living_room")
    
    @patch('home_assistant.requests.post')
    def test_request_exception(self, mock_post, mock_interface):
        """Test handling of request exceptions"""
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Error when attempting"):
            mock_interface.turn_on_lights("light.living_room")


class TestHelperMethods:
    """Test internal helper methods: _call_ha_service and _handle_on_off_entity"""
    
    # Tests for _call_ha_service
    @patch('home_assistant.requests.post')
    def test_call_ha_service_success(self, mock_post, mock_interface):
        """Test _call_ha_service with successful API call"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface._call_ha_service(
            domain="switch",
            service="turn_on",
            entity_id="switch.test",
            operation_description="turn on test switch"
        )
        
        # Verify the correct API call was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        assert "switch/turn_on" in call_args[0][0]
        
        # Check headers
        assert call_args[1]['headers']['Authorization'] == f"Bearer {mock_interface.access_token}"
        assert call_args[1]['headers']['Content-Type'] == "application/json"
        
        # Check payload
        assert call_args[1]['json']['entity_id'] == "switch.test"
    
    @patch('home_assistant.requests.post')
    def test_call_ha_service_different_domains(self, mock_post, mock_interface):
        """Test _call_ha_service works with different domains"""
        mock_post.return_value = MockResponse({}, 200)
        
        # Test with fan domain
        mock_interface._call_ha_service("fan", "turn_off", "fan.bedroom", "turn off fan")
        assert "fan/turn_off" in mock_post.call_args[0][0]
        
        # Test with light domain
        mock_post.reset_mock()
        mock_interface._call_ha_service("light", "turn_on", "light.kitchen", "turn on light")
        assert "light/turn_on" in mock_post.call_args[0][0]
    
    @patch('home_assistant.requests.post')
    def test_call_ha_service_failure(self, mock_post, mock_interface):
        """Test _call_ha_service handles API failures"""
        mock_post.return_value = MockResponse({"error": "Service not found"}, 404)
        
        with pytest.raises(Exception, match="Failed to"):
            mock_interface._call_ha_service(
                domain="invalid",
                service="invalid_service",
                entity_id="invalid.entity",
                operation_description="invalid operation"
            )
    
    @patch('home_assistant.requests.post')
    def test_call_ha_service_network_error(self, mock_post, mock_interface):
        """Test _call_ha_service with network error"""
        mock_post.side_effect = Exception("Network timeout")
        
        with pytest.raises(Exception, match="Error when attempting"):
            mock_interface._call_ha_service(
                domain="light",
                service="turn_off",
                entity_id="light.test",
                operation_description="turn off light.test"
            )
    
    # Tests for _handle_on_off_entity
    @patch('home_assistant.requests.post')
    def test_handle_on_off_entity_switch_on(self, mock_post, mock_interface):
        """Test _handle_on_off_entity turns on a switch"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface._handle_on_off_entity(
            entity_id="switch.outlet",
            entity_point="state",
            value=1,
            entity_kind="switch"
        )
        
        # Should call turn_on_switch
        mock_post.assert_called_once()
        assert "switch/turn_on" in mock_post.call_args[0][0]
    
    @patch('home_assistant.requests.post')
    def test_handle_on_off_entity_switch_off(self, mock_post, mock_interface):
        """Test _handle_on_off_entity turns off a switch"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface._handle_on_off_entity(
            entity_id="switch.outlet",
            entity_point="state",
            value=0,
            entity_kind="switch"
        )
        
        # Should call turn_off_switch
        mock_post.assert_called_once()
        assert "switch/turn_off" in mock_post.call_args[0][0]
    
    @patch('home_assistant.requests.post')
    def test_handle_on_off_entity_fan_on(self, mock_post, mock_interface):
        """Test _handle_on_off_entity turns on a fan"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface._handle_on_off_entity(
            entity_id="fan.bedroom",
            entity_point="state",
            value=1,
            entity_kind="fan"
        )
        
        # Should call turn_on_fan
        mock_post.assert_called_once()
        assert "fan/turn_on" in mock_post.call_args[0][0]
    
    @patch('home_assistant.requests.post')
    def test_handle_on_off_entity_fan_off(self, mock_post, mock_interface):
        """Test _handle_on_off_entity turns off a fan"""
        mock_post.return_value = MockResponse({}, 200)
        
        mock_interface._handle_on_off_entity(
            entity_id="fan.bedroom",
            entity_point="state",
            value=0,
            entity_kind="fan"
        )
        
        # Should call turn_off_fan
        mock_post.assert_called_once()
        assert "fan/turn_off" in mock_post.call_args[0][0]
    
    def test_handle_on_off_entity_invalid_point(self, mock_interface):
        """Test _handle_on_off_entity rejects non-state points"""
        with pytest.raises(ValueError, match="Unsupported entity point"):
            mock_interface._handle_on_off_entity(
                entity_id="switch.outlet",
                entity_point="brightness",  # Invalid for switch
                value=1,
                entity_kind="switch"
            )
    
    def test_handle_on_off_entity_invalid_value_not_int(self, mock_interface):
        """Test _handle_on_off_entity rejects non-integer values"""
        with pytest.raises(ValueError, match="must be 1 \\(on\\) or 0 \\(off\\)"):
            mock_interface._handle_on_off_entity(
                entity_id="switch.outlet",
                entity_point="state",
                value="on",  # String instead of int
                entity_kind="switch"
            )
    
    def test_handle_on_off_entity_invalid_value_out_of_range(self, mock_interface):
        """Test _handle_on_off_entity rejects values other than 0 or 1"""
        with pytest.raises(ValueError, match="must be 1 \\(on\\) or 0 \\(off\\)"):
            mock_interface._handle_on_off_entity(
                entity_id="switch.outlet",
                entity_point="state",
                value=5,  # Invalid value
                entity_kind="switch"
            )
    
    def test_handle_on_off_entity_unsupported_kind(self, mock_interface):
        """Test _handle_on_off_entity rejects unsupported entity kinds"""
        with pytest.raises(ValueError, match="Unsupported entity kind"):
            mock_interface._handle_on_off_entity(
                entity_id="climate.thermostat",
                entity_point="state",
                value=1,
                entity_kind="thermostat"  # Not supported by this handler
            )
    
    @patch('home_assistant.requests.post')
    def test_handle_on_off_entity_all_entity_kinds(self, mock_post, mock_interface):
        """Test _handle_on_off_entity supports both switch and fan"""
        mock_post.return_value = MockResponse({}, 200)
        
        # Test switch
        mock_interface._handle_on_off_entity("switch.test", "state", 1, "switch")
        assert "switch/turn_on" in mock_post.call_args[0][0]
        
        # Test fan
        mock_post.reset_mock()
        mock_interface._handle_on_off_entity("fan.test", "state", 1, "fan")
        assert "fan/turn_on" in mock_post.call_args[0][0]


class TestUserWrittenTestsMocked:
    """
    Mock versions of the integration tests you wrote.
    These simulate the Platform Driver calling your interface methods.
    """
    
    @patch('home_assistant.requests.get')
    def test_get_switch_state(self, mock_get, mock_interface):
        """
        Mock version of test_get_switch_state
        Simulates: agent.vip.rpc.call(PLATFORM_DRIVER, 'get_point', 'home_assistant', 'switch_state')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        switch_reg = HomeAssistantRegister(
            True, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=switch_reg)
        
        # Mock Home Assistant API response - switch is OFF
        mock_get.return_value = MockResponse({
            "state": "off",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling get_point
        result = mock_interface.get_point("switch_state")
        
        # get_point returns 0 when attribute is not found
        assert result == 0, f"Expected switch to be OFF (0), got {result}"
    
    @patch('home_assistant.requests.post')
    @patch('home_assistant.requests.get')
    def test_set_switch_on(self, mock_get, mock_post, mock_interface):
        """
        Mock version of test_set_switch_on
        Simulates: 
        1. agent.vip.rpc.call(PLATFORM_DRIVER, 'set_point', 'home_assistant', 'switch_state', 1)
        2. agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        switch_reg = HomeAssistantRegister(
            False, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=switch_reg)
        mock_interface.get_registers_by_type = Mock(return_value=[switch_reg])
        
        # Mock successful turn_on call
        mock_post.return_value = MockResponse({}, 200)
        
        # Simulate Platform Driver calling set_point to turn ON
        mock_interface._set_point("switch_state", 1)
        
        # Verify the correct API call was made
        assert mock_post.called
        assert "switch/turn_on" in mock_post.call_args[0][0]
        
        # Mock Home Assistant API response after switch is ON
        mock_get.return_value = MockResponse({
            "state": "on",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling scrape_all
        result = mock_interface._scrape_all()
        
        # Your test expects: {'switch_state': 1}
        assert result.get("switch_state") == 1, (
            f"Expected switch_state to be 1 (ON), got {result.get('switch_state')}"
        )
    
    @patch('home_assistant.requests.post')
    @patch('home_assistant.requests.get')
    def test_set_switch_off(self, mock_get, mock_post, mock_interface):
        """
        Mock version of test_set_switch_off
        Simulates:
        1. agent.vip.rpc.call(PLATFORM_DRIVER, 'set_point', 'home_assistant', 'switch_state', 0)
        2. agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        switch_reg = HomeAssistantRegister(
            False, "switch_state", "On/Off", int, {},
            "switch.outlet", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=switch_reg)
        mock_interface.get_registers_by_type = Mock(return_value=[switch_reg])
        
        # Mock successful turn_off call
        mock_post.return_value = MockResponse({}, 200)
        
        # Simulate Platform Driver calling set_point to turn OFF
        mock_interface._set_point("switch_state", 0)
        
        # Verify the correct API call was made
        assert mock_post.called
        assert "switch/turn_off" in mock_post.call_args[0][0]
        
        # Mock Home Assistant API response after switch is OFF
        mock_get.return_value = MockResponse({
            "state": "off",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling scrape_all
        result = mock_interface._scrape_all()
        
        # Your test expects: {'switch_state': 0}
        assert result.get("switch_state") == 0, (
            f"Expected switch_state to be 0 (OFF), got {result.get('switch_state')}"
        )
    
    @patch('home_assistant.requests.get')
    def test_get_fan_state(self, mock_get, mock_interface):
        """
        Mock version of test_get_fan_state
        Simulates: agent.vip.rpc.call(PLATFORM_DRIVER, 'get_point', 'home_assistant', 'fan_state')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        fan_reg = HomeAssistantRegister(
            True, "fan_state", "On/Off", int, {},
            "fan.bedroom", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=fan_reg)
        
        # Mock Home Assistant API response - fan is OFF
        mock_get.return_value = MockResponse({
            "state": "off",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling get_point
        result = mock_interface.get_point("fan_state")
        
        # get_point returns 0 when the attribute is not found
        assert result == 0, f"Expected fan to be OFF (0), got {result}"
    
    @patch('home_assistant.requests.post')
    @patch('home_assistant.requests.get')
    def test_set_fan_on(self, mock_get, mock_post, mock_interface):
        """
        Mock version of test_set_fan_on
        Simulates:
        1. agent.vip.rpc.call(PLATFORM_DRIVER, 'set_point', 'home_assistant', 'fan_state', 1)
        2. agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        fan_reg = HomeAssistantRegister(
            False, "fan_state", "On/Off", int, {},
            "fan.bedroom", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=fan_reg)
        mock_interface.get_registers_by_type = Mock(return_value=[fan_reg])
        
        # Mock successful turn_on call
        mock_post.return_value = MockResponse({}, 200)
        
        # Simulate Platform Driver calling set_point to turn ON
        mock_interface._set_point("fan_state", 1)
        
        # Verify the correct API call was made
        assert mock_post.called
        assert "fan/turn_on" in mock_post.call_args[0][0]
        
        # Mock Home Assistant API response after fan is ON
        mock_get.return_value = MockResponse({
            "state": "on",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling scrape_all
        result = mock_interface._scrape_all()
        
        # Your test expects: {'fan_state': 1}
        assert result.get("fan_state") == 1, (
            f"Expected fan_state to be 1 (ON), got {result.get('fan_state')}"
        )
    
    @patch('home_assistant.requests.post')
    @patch('home_assistant.requests.get')
    def test_set_fan_off(self, mock_get, mock_post, mock_interface):
        """
        Mock version of test_set_fan_off
        Simulates:
        1. agent.vip.rpc.call(PLATFORM_DRIVER, 'set_point', 'home_assistant', 'fan_state', 0)
        2. agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant')
        """
        from home_assistant import HomeAssistantRegister
        
        # Set up the register
        fan_reg = HomeAssistantRegister(
            False, "fan_state", "On/Off", int, {},
            "fan.bedroom", "state"
        )
        mock_interface.get_register_by_name = Mock(return_value=fan_reg)
        mock_interface.get_registers_by_type = Mock(return_value=[fan_reg])
        
        # Mock successful turn_off call
        mock_post.return_value = MockResponse({}, 200)
        
        # Simulate Platform Driver calling set_point to turn OFF
        mock_interface._set_point("fan_state", 0)
        
        # Verify the correct API call was made
        assert mock_post.called
        assert "fan/turn_off" in mock_post.call_args[0][0]
        
        # Mock Home Assistant API response after fan is OFF
        mock_get.return_value = MockResponse({
            "state": "off",
            "attributes": {}
        }, 200)
        
        # Simulate Platform Driver calling scrape_all
        result = mock_interface._scrape_all()
        
        # Your test expects: {'fan_state': 0}
        assert result.get("fan_state") == 0, (
            f"Expected fan_state to be 0 (OFF), got {result.get('fan_state')}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
