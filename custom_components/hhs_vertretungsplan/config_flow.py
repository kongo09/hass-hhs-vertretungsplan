"""The HHS Vertretungsplan component."""
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from hhs_vertretungsplan_parser.vertretungsplan_parser import HHSVertretungsplanParser, AuthenticationException

from aiohttp.client_exceptions import ClientConnectorError

from typing import Any

import logging
import voluptuous as vol

from .const import CONF_PASS, CONF_TUTOR_GROUP, CONF_USER, DOMAIN

_LOGGER = logging.getLogger(__name__)



class HHSVertretungsplanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for HHS Vertretungsplan."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self.hhs: HHSVertretungsplanParser = None


    def _get_schema(self, user_input):
        """Provide schema for user input."""
        schema = vol.Schema({
            vol.Required(CONF_TUTOR_GROUP, default=user_input[CONF_TUTOR_GROUP]): cv.string,
            vol.Required(CONF_USER, default=user_input[CONF_USER]): cv.string,
            vol.Required(CONF_PASS, default=user_input[CONF_PASS]): cv.string
        })
        return schema


    async def async_step_user(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Handle initial step of user config flow."""

        errors = {}

        # user input was provided, so check and save it
        if user_input is not None:
            try:
                # let's try and connect to HHS
                session = async_get_clientsession(self.hass)
                user = user_input[CONF_USER]
                password = user_input[CONF_PASS]
                self.hhs = HHSVertretungsplanParser(session, user, password)

                # try to load some data
                await self.hhs.load_data()

                # use the tutor_group as unique_id
                unique_id = DOMAIN + "_" + user_input[CONF_TUTOR_GROUP].strip()

                # set the unique id for the entry, abort if it already exists
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # compile a name from model and serial
                return self.async_create_entry(
                    title=unique_id,
                    data=user_input
                )

            except (ConnectionError, ClientConnectorError, AuthenticationException) as e:
                errors['base'] = "authentication"

        if user_input is None:
            user_input = {}

        # no user_input so far
        # what to ask the user
        schema = self._get_schema(user_input)

        # show the form to the user
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)