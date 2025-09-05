from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from textual import work
from textual.containers import VerticalGroup
from textual.widgets import Label, ListItem, ListView


class SerialPortListItem(ListItem):
    """Individual port info."""

    DEFAULT_CSS = """
        SerialPortListItem {
            padding: 1 1;
            border: solid gray;
        }

        .port-id {
            text-style: bold underline;
        }

        .port-desc {
            color: $text-muted;
        }

        .port-hwid {
            color: $text-muted;
        }
    """

    def __init__(self, port_info: ListPortInfo, *args, **kwargs):
        component = VerticalGroup(
            Label(f"{port_info.name}", classes="port-id"),
            Label(f"Description: {port_info.description}", classes="port-desc"),
            Label(f"HWID: {port_info.hwid}", classes="port-hwid"),
        )
        super().__init__(component, *args, **kwargs)
        self._port_info = port_info

    @property
    def port_name(self):
        return self._port_info.name


class SerialPortListView(ListView):
    """List all available serial ports."""

    BORDER_TITLE = "Serial Ports"

    DEFAULT_CSS = """
    SerialPortListView {
        dock: left;
        width: 30%;
        height: 100%;
        border: round $secondary;
    }
    """

    BINDINGS = [
        ("enter", "app.connect_serial_port", "Connect"),
        ("c", "app.configure_connection", "Configure"),
    ]

    def on_mount(self):
        self.loading = True
        self.load_ports()

    def on_focus(self):
        self.app.refresh_bindings()

    @work
    async def load_ports(self):
        self.extend([SerialPortListItem(port) for port in comports()])
        self.loading = False

    # TODO: Add search / filtering
