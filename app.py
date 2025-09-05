import asyncio

import widgets
from serial import Serial
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive, var
from textual.widgets import Footer


class SerViewApp(App):
    DEFAULT_CSS = """
    Input {
            width: 100%;
        }
    """

    BINDINGS = [
        ("ctrl+l", "toggle_port_list", "Toggle Port List"),
        Binding("ctrl+d", "disconnect", "Disconnect", priority=True),
    ]

    serial_port = var(None)
    connected = reactive(False, bindings=True)
    endline = var("\n")
    serial_worker = var(None)

    def compose(self) -> ComposeResult:
        with Container():
            yield widgets.SerialPortListView(id="ports-list")
            yield widgets.SerialMessageBox()
        yield widgets.OutgoingMsg(placeholder="Outgoing message", id="msg-input")
        yield Footer()

    def on_mount(self):
        self.theme = "tokyo-night"
        self.query_one("#ports-list").focus()

    @on(widgets.OutgoingMsg.Submitted)
    def action_send_outgoing_msg(self):
        input: widgets.OutgoingMsg = self.query_one("#msg-input")
        msg_box = self.query_one(widgets.SerialMessageBox)
        if not self.serial_port:
            self.notify(
                "No serial port connected!", title="Not Connected", severity="error"
            )
            return
        self.serial_port.write((input.value + self.endline).encode())
        msg_box.add_message(input.value, outgoing=True)
        input.clear()

    def action_toggle_port_list(self):
        port_list = self.query_one(widgets.SerialPortListView)
        port_list.display = not port_list.display
        if port_list.display:
            port_list.focus()

    async def action_connect_serial_port(self):
        ports_list = self.query_one(widgets.SerialPortListView)
        selected_port: widgets.SerialPortListItem | None = ports_list.highlighted_child
        if not selected_port:
            self.notify(
                "Use the arrow keys to select a port to connect to",
                title="No port selected!",
                severity="error",
            )
            return
        # TODO: Make serial connection configurable!
        self.serial_port = Serial(selected_port.port_name, baudrate=115200)
        self.connected = True
        self.query_one("#msg-input").focus()
        self.notify(f"Connected to {selected_port.port_name}", title="Connected!")

    def action_configure_connection(self):
        self.notify(
            "Feature coming soon... maybe", title="NOT IMPLEMENTED", severity="warning"
        )

    async def action_next_baud_rate(self):
        pass

    async def action_prev_baud_rate(self):
        pass

    def watch_connected(self, connected: bool):
        if connected:
            self.serial_worker = self._listen_for_incoming_msg()
        else:
            try:
                if self.serial_worker:
                    self.serial_worker.cancel()
            except ValueError:
                # This will run upon app instantiaton, when binding does not yet exist
                pass
            finally:
                if self.serial_port:
                    self.serial_port.close()
                self.serial_port = None
        input_field = self.query_one("#msg-input")
        input_field.disabled = not connected

    def action_disconnect(self):
        self.connected = False
        self.notify("Disconnected!", severity="warning")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        match action:
            case "disconnect":
                return self.connected
            case "connect_serial_port":
                return not self.connected
            case _:
                return True

    @work(exclusive=True)
    async def _listen_for_incoming_msg(self):
        if not self.serial_port:
            self.notify("No serial port connected!", severity="error")
            return
        msg_box = self.query_one(widgets.SerialMessageBox)
        while self.connected:
            if self.serial_port.in_waiting:
                data = self.serial_port.read_all()
                msg_box.add_message(data.decode(errors="ignore"))
            await asyncio.sleep(0.1)


def main():
    SerViewApp().run()


if __name__ == "__main__":
    main()
