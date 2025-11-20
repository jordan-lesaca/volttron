# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2023 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

import json
import logging
import pytest
import gevent

from volttron.platform.agent.known_identities import (
    PLATFORM_DRIVER,
    CONFIGURATION_STORE,
)
from volttron.platform import get_services_core
from volttron.platform.agent import utils
from volttron.platform.keystore import KeyStore
from volttrontesting.utils.platformwrapper import PlatformWrapper

utils.setup_logging()
logger = logging.getLogger(__name__)

# To run these tests, create a helper toggle named volttrontest in your Home Assistant instance.
# This can be done by going to Settings > Devices & services > Helpers > Create Helper > Toggle
HOMEASSISTANT_TEST_IP = ""
ACCESS_TOKEN = ""
PORT = ""

skip_msg = "Some configuration variables are not set. Check HOMEASSISTANT_TEST_IP, ACCESS_TOKEN, and PORT"

# Skip tests if variables are not set
pytestmark = pytest.mark.skipif(
    not (HOMEASSISTANT_TEST_IP and ACCESS_TOKEN and PORT),
    reason=skip_msg
)
HOMEASSISTANT_DEVICE_TOPIC = "devices/home_assistant"


# Get the point which will should be off
def test_get_point(volttron_instance, config_store):
    expected_values = 0
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(PLATFORM_DRIVER, 'get_point', 'home_assistant', 'bool_state').get(timeout=20)
    assert result == expected_values, "The result does not match the expected result."


# The default value for this fake light is 3. If the test cannot reach out to home assistant,
# the value will default to 3 making the test fail.
def test_data_poll(volttron_instance: PlatformWrapper, config_store):
    expected_values = [{'bool_state': 0}, {'bool_state': 1}]
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant').get(timeout=20)
    assert result in expected_values, "The result does not match the expected result."


# Turn on the light. Light is automatically turned off every 30 seconds to allow test to turn
# it on and receive the correct value.
def test_set_point(volttron_instance, config_store):
    expected_values = {'bool_state': 1}
    agent = volttron_instance.dynamic_agent
    agent.vip.rpc.call(PLATFORM_DRIVER, 'set_point', 'home_assistant', 'bool_state', 1)
    gevent.sleep(10)
    result = agent.vip.rpc.call(PLATFORM_DRIVER, 'scrape_all', 'home_assistant').get(timeout=20)
    assert result == expected_values, "The result does not match the expected result."

def test_get_switch_state(volttron_instance, config_store):
    """Switch shuold initially be OFF (0)."""
    expected = 0
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 
        'get_point', 
        'home_assistant', 
        'switch_state'
    ).get(timeout=20)
    assert result == expected, f"Expected switch to be OFF (0), got {result}"

def test_set_switch_on(volttron_instance, config_store):
    """Set the switch to ON (1) and verify via scrape_all."""
    agent = volttron_instance.dynamic_agent
    
    # Set the switch_state point to 1 (ON)
    agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "set_point",
        "home_assistant",
        "switch_state",
        1,
    )

    # Give Home Assistant time to update
    gevent.sleep(10)

    # Scrape all points and check the switch_state value
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "scrape_all",
        "home_assistant",
    ).get(timeout=20)

    assert result.get("switch_state") == 1, (
        f"Expected switch_state to be 1 (ON), got {result.get('switch_state')}"
    )

def test_set_switch_off(volttron_instance, config_store):
    """Set the switch to OFF (0) and verify via scrape_all."""
    agent = volttron_instance.dynamic_agent

    # Set the switch_state point to 0 (OFF)
    agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "set_point",
        "home_assistant",
        "switch_state",
        0,
    )

    # Give Home Assistant time to update
    gevent.sleep(10)

    # Scrape all points and check the switch_state value
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "scrape_all",
        "home_assistant",
    ).get(timeout=20)

    assert result.get("switch_state") == 0, (
        f"Expected switch_state to be 0 (OFF), got {result.get('switch_state')}"
    )

def test_get_fan_state(volttron_instance, config_store):
    """Fan should initially be OFF (0)."""
    expected = 0
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "get_point",
        "home_assistant",
        "fan_state",
    ).get(timeout=20)
    assert result == expected, f"Expected fan to be OFF (0), got {result}"


def test_set_fan_on(volttron_instance, config_store):
    """Set the fan to ON (1) and verify via scrape_all."""
    agent = volttron_instance.dynamic_agent

    agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "set_point",
        "home_assistant",
        "fan_state",
        1,
    )
    gevent.sleep(10)

    result = agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "scrape_all",
        "home_assistant",
    ).get(timeout=20)

    assert result.get("fan_state") == 1, (
        f"Expected fan_state to be 1 (ON), got {result.get('fan_state')}"
    )


def test_set_fan_off(volttron_instance, config_store):
    """Set the fan to OFF (0) and verify via scrape_all."""
    agent = volttron_instance.dynamic_agent

    agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "set_point",
        "home_assistant",
        "fan_state",
        0,
    )
    gevent.sleep(10)

    result = agent.vip.rpc.call(
        PLATFORM_DRIVER,
        "scrape_all",
        "home_assistant",
    ).get(timeout=20)

    assert result.get("fan_state") == 0, (
        f"Expected fan_state to be 0 (OFF), got {result.get('fan_state')}"
    )    

@pytest.fixture(scope="module")
def config_store(volttron_instance, platform_driver):

    capabilities = [{"edit_config_store": {"identity": PLATFORM_DRIVER}}]
    volttron_instance.add_capabilities(volttron_instance.dynamic_agent.core.publickey, capabilities)

    registry_config = "homeassistant_test.json"
    registry_obj = [{
        "Entity ID": "input_boolean.volttrontest",
        "Entity Point": "state",
        "Volttron Point Name": "bool_state",
        "Units": "On / Off",
        "Units Details": "off: 0, on: 1",
        "Writable": True,
        "Starting Value": 3,
        "Type": "int",
        "Notes": "lights hallway"
    }]

    volttron_instance.dynamic_agent.vip.rpc.call(CONFIGURATION_STORE,
                                                 "manage_store",
                                                 PLATFORM_DRIVER,
                                                 registry_config,
                                                 json.dumps(registry_obj),
                                                 config_type="json")
    gevent.sleep(2)
    # driver config
    driver_config = {
        "driver_config": {"ip_address": HOMEASSISTANT_TEST_IP, "access_token": ACCESS_TOKEN, "port": PORT},
        "driver_type": "home_assistant",
        "registry_config": f"config://{registry_config}",
        "timezone": "US/Pacific",
        "interval": 30,
    }

    volttron_instance.dynamic_agent.vip.rpc.call(CONFIGURATION_STORE,
                                                 "manage_store",
                                                 PLATFORM_DRIVER,
                                                 HOMEASSISTANT_DEVICE_TOPIC,
                                                 json.dumps(driver_config),
                                                 config_type="json"
                                                 )
    gevent.sleep(2)

    yield platform_driver

    print("Wiping out store.")
    volttron_instance.dynamic_agent.vip.rpc.call(CONFIGURATION_STORE, "manage_delete_store", PLATFORM_DRIVER)
    gevent.sleep(0.1)


@pytest.fixture(scope="module")
def platform_driver(volttron_instance):
    # Start the platform driver agent which would in turn start the bacnet driver
    platform_uuid = volttron_instance.install_agent(
        agent_dir=get_services_core("PlatformDriverAgent"),
        config_file={
            "publish_breadth_first_all": False,
            "publish_depth_first": False,
            "publish_breadth_first": False,
        },
        start=True,
    )
    gevent.sleep(2)  # wait for the agent to start and start the devices
    assert volttron_instance.is_agent_running(platform_uuid)
    yield platform_uuid

    volttron_instance.stop_agent(platform_uuid)
    if not volttron_instance.debug_mode:
        volttron_instance.remove_agent(platform_uuid)
