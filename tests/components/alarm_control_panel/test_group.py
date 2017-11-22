"""The tests for the manual Alarm Control Panel component."""
from datetime import timedelta
import unittest
from unittest.mock import patch

from homeassistant.setup import setup_component
from homeassistant.const import (
    STATE_ALARM_DISARMED, STATE_ALARM_ARMED_HOME, STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT, STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_PENDING, STATE_ALARM_TRIGGERED)
import homeassistant.components.alarm_control_panel as alarm

import homeassistant.util.dt as dt_util

from tests.common import (
    assert_setup_component, fire_time_changed, get_test_home_assistant)

CODE = '1234'
TAMPER_CODE = '123456'
TAMPER_CODE_TEMPLATE = '{{ "" if from_state != "triggered" else "123456" }}'


class TestAlarmControlPanelGroup(unittest.TestCase):
    """Test the group alarm module."""

    def setUp(self):  # pylint: disable=invalid-name
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        with assert_setup_component(5):
            setup_component(self.hass, alarm.DOMAIN, {
                'alarm_control_panel': [{
                    # The living room doesn't do anything special
                    'platform': 'manual',
                    'name': 'livingroom',
                    'code': CODE,
                    'pending_time': 0,
                    'disarmed': {
                        'trigger_time': 0
                    }
                }, {
                    # The garage gives you some time to come and go,
                    # except at night
                    'platform': 'manual',
                    'name': 'garage',
                    'code': CODE,
                    'delay_time': 30,
                    'armed_night': {
                        'delay_time': 0,
                        'pending_time': 0
                    },
                    'disarmed': {
                        'trigger_time': 0
                    }
                }, {
                    # The bedroom is turned off at night
                    'platform': 'manual',
                    'name': 'bedroom',
                    'code': CODE,
                    'armed_night': {
                        'trigger_time': 0
                    },
                    'disarmed': {
                        'trigger_time': 0
                    }
                }, {
                    # The tampering switch is turned off by a special code,
                    # and triggers the siren even if the alarm is not armed
                    'platform': 'manual',
                    'name': 'tamper',
                    'code_template': TAMPER_CODE_TEMPLATE,
                }, {
                    'platform': 'group',
                    'name': 'testgroup',
                    'panels': [
                        {'panel': 'alarm_control_panel.livingroom'},
                        {'panel': 'alarm_control_panel.garage'},
                        {'panel': 'alarm_control_panel.bedroom'},
                        {'panel': 'alarm_control_panel.tamper'},
                    ]
                }]
            })

        self.hass.start()
        self.hass.block_till_done()

    def tearDown(self):  # pylint: disable=invalid-name
        """Stop down everything that was started."""
        self.hass.stop()

    def test_create(self):
        """Basic test for state method."""
        entity_id = 'alarm_control_panel.testgroup'
        self.assertEqual(STATE_ALARM_DISARMED,
                         self.hass.states.get(entity_id).state)
