from tkinter import ttk


class PlaceholderScreen(ttk.Frame):
    """Temporary screen for v1.0 — confirms that the window opens and services are connected.
    It will be replaced by the login/registration screen in v1.1."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app

        ttk.Label(self, text="BookByteStore", font=("", 20, "bold")).pack(pady=(40, 10))
        ttk.Label(self, text="The GUI framework is operational. Services are connected:").pack(pady=(0, 16))

        services_frame = ttk.Frame(self)
        services_frame.pack()
        for name in ("auth", "catalog", "purchase", "admin"):
            service = getattr(self.app.services, name)
            ttk.Label(services_frame, text=f"✓ {name}: {type(service).__name__}").pack(anchor="w")
