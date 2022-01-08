"""The HHS Vertretungsplan component."""
from __future__ import annotations
from typing import Dict
from datetime import datetime, timedelta, timezone
from babel.dates import format_date, format_datetime
from dataclasses import asdict

from hhs_vertretungsplan_parser.vertretungsplan_parser import AuthenticationException, HHSVertretungsplanParser

from .const import *

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN] = dict()
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup HHS Vertretungsplan from a config entry."""

    # setup the parser
    session = async_get_clientsession(hass)
    user = entry.data[CONF_USER]
    password = entry.data[CONF_PASS]
    hhs = HHSVertretungsplanParser(session, user, password)
    await hhs.load_data()

    # setup a coordinator
    coordinator = HHSDataUpdateCoordinator(hass, _LOGGER, hhs, timedelta(seconds=POLLING_INTERVAL))

    # refresh coordinator for the first time to load initial data
    await coordinator.async_config_entry_first_refresh()
    
    # store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # setup sensors
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)

    hass.data[DOMAIN].pop(entry.entry_id)

    return True


class HHSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vertretungsplan data from the HHS."""

    def __init__(self, hass: HomeAssistant, _LOGGER, hhs: HHSVertretungsplanParser, update_interval: timedelta) -> None:
        """Initialize."""

        self.hhs = hhs
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)


    async def _async_update_data(self) -> Dict:
        """Update data via library."""
        _LOGGER.debug(f"_async_update_data() called")

        """Only update in time window."""
        # todo: allow forced update
        try:
            now = datetime.now().time()
            start = datetime.strptime(POLLING_START, '%H:%M').time()
            _LOGGER.debug(f"start={start}")
            end = datetime.strptime(POLLING_END, '%H:%M').time()
            _LOGGER.debug(f"end={end}")
            if self.data is not None and (now < start or now > end):
                _LOGGER.debug(f"Time is outside polling window, skipping update")
                return self.data
        except (Exception) as error:
            # in case something goes wrong with date/time parsing, we just update the data and continue
            _LOGGER.error(f"Error occured with time parsing and comparison on update: {error}\n"
                          f"Start and end times should be in format 'HH:MM'.\n"
                          f"Configured are POLLING_START={POLLING_START} and POLLING_END={POLLING_END}\n"
                          f"Please inform the maintainer of the integration.")
            pass

        try:
            """Ask the library to reload fresh data."""
            await self.hhs.load_data()
            _LOGGER.debug(f"data loaded")
        except (ConnectionError, AuthenticationException) as error:
            raise UpdateFailed(error) from error

        """Let's return the raw list of all Vertretungen."""
        today = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        vertretungen = self.hhs.vertretungen
        klassenliste = {}
        for vertretung in vertretungen:
            # skip old stuff before today
            if vertretung.datum < today:
                continue
            # add to our list
            if vertretung.klasse in klassenliste:
                klassenliste[vertretung.klasse].append(asdict(vertretung))
            else:
                klassenliste[vertretung.klasse] = [asdict(vertretung)]

        """Now put it all together."""
        extra_states = {
            ATTR_VERTRETUNG: klassenliste,
            ATTR_STATUS: self.hhs.status
        }
        return extra_states