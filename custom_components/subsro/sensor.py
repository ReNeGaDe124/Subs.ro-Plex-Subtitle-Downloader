from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
import logging
import async_timeout
from .const import DOMAIN, DEVICE_NAME, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SubsroStatusSensor(entry, config)])

class SubsroStatusSensor(SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, entry, config):
        self._entry = entry
        self._config = config
        self._attr_name = "Status"
        self._attr_unique_id = "subsro_plex_subtitle_downloader_status"
        self._attr_native_value = "Idle"
        
        self._attr_should_poll = True 
        
        self._attr_extra_state_attributes = {
            "last_action": "-",
            "last_item": "-",
            "subtitle_downloaded": "-",
            "last_run": "-",
            "log_output": ""
        }

    @property
    def icon(self):
        if self._attr_native_value == "Offline":
            return "mdi:alert"
        if self._attr_native_value == "Processing":
            return "mdi:sync"
        return "mdi:pulse"

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._handle_update)
        )

    @callback
    def _handle_update(self, data):
        if "activity" in data:
            self._attr_native_value = data["activity"]
        
        new_attrs = dict(self._attr_extra_state_attributes)
        
        if "item" in data and data["item"]:
            new_attrs["last_item"] = data["item"]
        if "timestamp" in data:
            new_attrs["last_run"] = data["timestamp"]
        if "log" in data:
            new_attrs["log_output"] = data["log"]
        if "action" in data:
            new_attrs["last_action"] = data["action"]
        if "result" in data:
            new_attrs["subtitle_downloaded"] = data["result"]
            
        self._attr_extra_state_attributes = new_attrs
        self.async_write_ha_state()

    async def async_update(self):
        url = self._config["url"]
        session = self._config["session"]
        
        try:
            async with async_timeout.timeout(5):
                response = await session.get(f"{url}/health")
                
                if response.status == 200:
                    if self._attr_native_value == "Offline":
                        self._attr_native_value = "Idle"
                else:
                    self._attr_native_value = "Offline"
                    
        except Exception:
            self._attr_native_value = "Offline"

    @property
    def device_info(self) -> DeviceInfo:

        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=DEVICE_NAME)





