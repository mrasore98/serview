import asyncio

import widgets
from serial import Serial
from textual import on, work
from textual.app import App, ComposeResult
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
        ("l", "toggle_port_list", "Toggle Port List"),
    ]

    serial_port = var(None)
    connected = reactive(False)
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
            self.notify("No serial port connected!", severity="error")
            return
        self.serial_port.write((input.value + self.endline).encode())
        msg_box.add_message(input.value, outgoing=True)
        input.clear()

    def action_toggle_port_list(self):
        port_list = self.query_one(widgets.SerialPortListView)
        port_list.display = not port_list.display

    async def action_connect_serial_port(self):
        ports_list = self.query_one(widgets.SerialPortListView)
        selected_port: widgets.SerialPortListItem | None = ports_list.highlighted_child
        if not selected_port:
            self.notify("No port selected!", severity="error")
            return
        # TODO: Make serial connection configurable!
        self.serial_port = Serial(selected_port.port_name, baudrate=115200)
        self.connected = True
        self.query_one("#msg-input").focus()
        self.notify(f"Connected to {selected_port.port_name}")

    def action_configure_connection(self):
        self.notify("NOT IMPLEMENTED", severity="warning")

    async def action_next_baud_rate(self):
        pass

    async def action_prev_baud_rate(self):
        pass

    def watch_connected(self, conn: bool):
        disconnect_binding = ("d", "disconnect", "Disconnect")
        if conn:
            self.BINDINGS.append(disconnect_binding)
            self.serial_worker = self._listen_for_incoming_msg()
        else:
            try:
                self.BINDINGS.remove(disconnect_binding)
                if self.serial_worker:
                    self.serial_worker.cancel()
            except ValueError:
                # This will run upon app instantiaton, when binding does not yet exist
                pass
        self.refresh_bindings()

    def action_disconnect(self):
        self.connected = False

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
