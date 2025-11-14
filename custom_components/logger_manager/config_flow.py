from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_FILTER_PATTERNS, DEFAULT_FILTER_PATTERNS


class LoggerManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Logger Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # Only allow a single config entry
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            # No options needed, just create the entry
            return self.async_create_entry(title="Logger Manager", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return LoggerManagerOptionsFlowHandler()
class LoggerManagerOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for runtime settings."""

    async def async_step_init(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            raw = user_input.get(CONF_FILTER_PATTERNS, [])

            # Accept either a list (new) or legacy string (old)
            if isinstance(raw, str):
                lines = [ln.strip() for ln in raw.splitlines()]
            elif isinstance(raw, list):
                lines = [str(x).strip() for x in raw]
            else:
                lines = []

            # Normalize, dedupe, and guardrail
            seen, extras = set(), []
            for p in lines:
                if not p:
                    continue
                if p == "*":
                    errors[CONF_FILTER_PATTERNS] = "too_broad"
                    continue
                if p not in seen:
                    seen.add(p)
                    extras.append(p)

            if not errors:
                return self.async_create_entry(
                    title="Logger Manager",
                    data={CONF_FILTER_PATTERNS: extras},
                )

        # Show the form
        current_extras = self.config_entry.options.get(CONF_FILTER_PATTERNS, [])
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_FILTER_PATTERNS,
                    default=current_extras or []
                ): selector.ObjectSelector()
            }),
            errors=errors,
        )
        
