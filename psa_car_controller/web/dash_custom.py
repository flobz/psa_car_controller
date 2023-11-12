from dash import Dash


class DashCustom(Dash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests_pathname_external_prefix = self.config.requests_pathname_prefix

    def _config(self):
        config = super()._config()
        # pieces of config needed by the front end
        config.update({
            "url_base_pathname": self.config.url_base_pathname,
            "requests_pathname_prefix": self.requests_pathname_external_prefix,
            "ui": self._dev_tools.ui,
            "props_check": self._dev_tools.props_check,
            "show_undo_redo": self.config.show_undo_redo,
            "suppress_callback_exceptions": self.config.suppress_callback_exceptions,
            "update_title": self.config.update_title,
        })
        if self._dev_tools.hot_reload:
            config["hot_reload"] = {
                # convert from seconds to msec as used by js `setInterval`
                "interval": int(self._dev_tools.hot_reload_interval * 1000),
                "max_retry": self._dev_tools.hot_reload_max_retry,
            }
        if self.validation_layout and not self.config.suppress_callback_exceptions:
            config["validation_layout"] = self.validation_layout

        return config
