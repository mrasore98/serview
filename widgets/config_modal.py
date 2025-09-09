from textual.widget import Widget
from textual.widgets import Footer, Input, Label, Static
from textual.screen import ModalScreen, Screen
from textual.containers import (
    CenterMiddle,
    Grid,
    Horizontal,
    HorizontalGroup,
    HorizontalScroll,
    Vertical,
    VerticalGroup,
)

from .css import CSS_DIR


class ConfigParameter(Widget):
    def __init__(self, label: str, input_widget: Widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = label
        self._input_widget = input_widget
        self._input_widget.add_class("config-input")

    def compose(self):
        yield Label(self._label, classes="config-label")
        yield self._input_widget


class ConnectionConfigModal(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Close")]
    CSS_PATH = CSS_DIR / "config_modal.tcss"

    def compose(self):
        with Grid(id="congfig-box"):
            yield ConfigParameter("Port", Input(placeholder="port"), id="port-config")
            yield ConfigParameter(
                "Baudrate", Input(placeholder="bautdrate"), id="baud-config"
            )
            yield ConfigParameter(
                "Parity", Input(placeholder="parity"), id="parity-config"
            )
        yield Footer()
