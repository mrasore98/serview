from datetime import datetime

from rich.text import Text
from textual.widgets import RichLog


class SerialMessageBox(RichLog, can_focus=False):
    """Scrollable container to record incoming and outgoing serial communication."""

    BORDER_TITLE = "Activity"

    DEFAULT_CSS = """
        SerialMessageBox {
            border: round $accent;
        }
    """

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
