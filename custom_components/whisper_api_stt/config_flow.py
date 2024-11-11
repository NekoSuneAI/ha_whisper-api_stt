import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_API_KEY, CONF_LANG, CONF_MODEL, CONF_URL, CONF_PROMPT, CONF_TEMPERATURE
import homeassistant.helpers.config_validation as cv

@config_entries.HANDLERS.register(DOMAIN)
class WhisperSTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whisper STT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Whisper STT", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): cv.string,
            vol.Optional(CONF_LANG, default="en-US"): cv.string,
            vol.Optional(CONF_MODEL, default="whisper-1"): cv.string,
            vol.Optional(CONF_URL, default="https://openai.nekosunevr.co.uk/v1/audio/transcriptions"): cv.string,
            vol.Optional(CONF_PROMPT, default=""): cv.string,
            vol.Optional(CONF_TEMPERATURE, default=0): vol.Coerce(float),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)
