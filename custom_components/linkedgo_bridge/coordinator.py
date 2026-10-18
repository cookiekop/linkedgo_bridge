"""DataUpdateCoordinator for our integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .xlink_ptp import PTPFields
from .hub import Hub
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DeviceEntity


_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    data: list[DeviceEntity]

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, hub: Hub
    ) -> None:
        """Initialize coordinator."""

        self.hub = hub
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        self.home_id = config_entry.data[PTPFields.HOME_ID]

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=self.poll_interval),
        )

        self.hub.on_update = lambda: self.async_set_updated_data(self.hub.devices)

    async def async_update_data(self) -> list[DeviceEntity]:
        try:
            return await self.hub.async_refresh(self.home_id)
        except Exception as err:
            raise UpdateFailed(f"Failed to request device state: {err}") from err
