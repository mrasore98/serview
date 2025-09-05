from textual.widgets import Input


class OutgoingMsg(Input):
    """Input wrapper for outgoing message field"""

    BINDINGS = [("enter", "submit", "Send")]

    BORDER_TITLE = "Send"

    DEFAULT_CSS = """
        OutgoingMsg {
            border: round $primary;
        }
    """
