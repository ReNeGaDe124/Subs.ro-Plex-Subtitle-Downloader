import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_URL, CONF_SECRET, DEFAULT_URL

class SubsroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Subs.ro Plex Subtitle Downloader", 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_URL, default=DEFAULT_URL): str,
                vol.Required(CONF_SECRET): str,
            })

        )
