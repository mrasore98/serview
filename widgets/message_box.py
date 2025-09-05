from datetime import datetime

import pyperclip
from rich.text import Text
from textual.widgets import RichLog


class SerialMessageBox(RichLog):
    """Scrollable container to record incoming and outgoing serial communication."""

    BORDER_TITLE = "Activity"

    DEFAULT_CSS = """
        SerialMessageBox {
            border: round $accent;
        }
    """

    BINDINGS = [
        ("y", "yank_contents", "Yank"),
        ("x", "clear_contents", "Clear"),
    ]

    def __init__(
        self,
        *args,
        include_timestamp: bool = True,
        timestamp_fmt: str = "%Y-%m-%d %H:%M:%S.%f",
        incoming_prefix: str = ">>>",
        outgoing_prefix: str = "<<<",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.include_timestamp = include_timestamp
        self.timestamp_fmt = timestamp_fmt
        self.incoming_prefix = incoming_prefix
        self.outgoing_prefix = outgoing_prefix

    def add_message(self, msg: str, outgoing: bool = False):
        prefix = self.outgoing_prefix if outgoing else self.incoming_prefix
        color = "cyan" if outgoing else "green"
        timestamp = (
            f"{datetime.now().strftime(self.timestamp_fmt)} "
            if self.include_timestamp
            else ""
        )

        message = Text.from_markup(
            f"[yellow]{timestamp}[/yellow][{color}]{prefix} {msg}[/{color}]"
        )

        self.write(message)

    def action_yank_contents(self):
        if not self.lines:
            self.notify("Nothing to yank!", title="Oops!", severity="error")
            return
        pyperclip.copy("\n".join([strip.text for strip in self.lines]))
        self.notify(f"Copied {len(self.lines)} to clipboard", title="Yank!")

    def action_clear_contents(self):
        self.clear()
        self.notify("Cleared the log area", title="Bye, logs!", severity="warning")
