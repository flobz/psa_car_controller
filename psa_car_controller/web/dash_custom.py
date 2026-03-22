from dash import Dash


class DashCustom(Dash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests_pathname_external_prefix = self.config.requests_pathname_prefix

    def _config(self):
        try:
            config = super()._config()
            # pieces of config needed by the front end
            config.update({
                "requests_pathname_prefix": self.requests_pathname_external_prefix,
            })
            if hasattr(self, "_dev_tools"):
                config.update({
                    "ui": getattr(self._dev_tools, "ui", True),
                    "props_check": getattr(self._dev_tools, "props_check", False),
                })
            return config
        except Exception:
            return self.config
