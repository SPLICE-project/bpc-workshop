from textual.widgets import Static, Header, Footer, Select, Log
from textual.app import App, ComposeResult
from textual import on
from textual.color import Color
import subprocess, socket, base64


OPTIONS = """Turn Lamp On
Turn Lamp Off
Dim Lamp
Brighten Lamp
Change Color White
Change Color Blue
Change Color Red
Change Color Green
Change Color Orange
Change Color Violet
Change Color Yellow
Change Color Purple
Change Color Aqua
Change Color Seafoam
Change Color Light Blue
Change Color Light Green
Change Color Light Purple
""".splitlines()

COLORS = [
    "#ffffff",
    "#0000ff",
    "#ff0000",
    "#00ff00",
    "#ffa500",
    "#ee82ee",
    "#ffff00",
    "#800080",
    "#00ffff",
    "#93e9be",
    "#00f5ff",
    "#90ee90",
    "#da70d6",
]

CONTROLLER_COMMANDS = [
    ("irsend SEND_ONCE lamp SWITCH_ON", "Turnedon"),
    ("irsend SEND_ONCE lamp SWITCH_OFF", "Turnedoff"),
    ("irsend SEND_ONCE lamp SWITCH_DIM", "Turneddim"),
    ("irsend SEND_ONCE lamp SWITCH_BRIGHT", "Turnedbright"),
    ("irsend SEND_ONCE lamp SWITCH_WHITE", "Turnedwhite"),
    ("irsend SEND_ONCE lamp SWITCH_BLUE", "Turnedblue"),
    ("irsend SEND_ONCE lamp SWITCH_RED", "Turnedred"),
    ("irsend SEND_ONCE lamp SWITCH_GREEN", "Turnedgreen"),
    ("irsend SEND_ONCE lamp SWITCH_ORANGE", "Turnedorange"),
    ("irsend SEND_ONCE lamp SWITCH_VIOLET", "Turnedviolet"),
    ("irsend SEND_ONCE lamp SWITCH_YELLOW", "Turnedyellow"),
    ("irsend SEND_ONCE lamp SWITCH_PURPLE", "Turnedpurple"),
    ("irsend SEND_ONCE lamp SWITCH_AQUA", "Turnedaqua"),
    ("irsend SEND_ONCE lamp SWITCH_SEAFOAM", "Turnedseafom"),
    ("irsend SEND_ONCE lamp SWITCH_LBLUE", "Turnedlightblue"),
    ("irsend SEND_ONCE lamp SWITCH_LGREEN", "Turnedlightgreen"),
    ("irsend SEND_ONCE lamp SWITCH_LPURPLE", "Turnedlightpurple")
]


def command(cmd_message):
  output = subprocess.check_output(cmd_message[0], stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
  send_packet(cmd_message[1])

def send_packet(message):
    host = ''
    port = 12345
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        dataLen = len(message)
        data = base64.b64encode(bytes(message, 'utf-8'))
        data = data * dataLen
        s.sendto(data, (host, port))

class LightBulbStatus(Static):
    recent_color = "#ffffff"
    #recent_alpha = "cc"
    recent_alpha = "cc"
    is_on = False

    def compose(self) -> ComposeResult:
        yield Static("Lightbulb status", classes="box")

    def update_status(self, status) -> None:
        bulb = self.query_one(Static)
        option_index = OPTIONS.index(status)

        command(CONTROLLER_COMMANDS[option_index]) # Send the command to the lamp
        # Update UI
        match option_index:
            case 0:
                bulb.styles.background = Color.parse(f"{self.recent_color}{self.recent_alpha}")
                bulb.styles.color = "black"
                self.is_on = True
            case 1:
                bulb.styles.background = Color.parse("#00000000")
                bulb.styles.color = "white"
                self.is_on = False
                # case 2: # Dim
                # bulb.styles.background = bulb.styles.background.darken(0.1)
                #
                #            case 3: # Brighten
            case _:
                if self.is_on:
                    self.recent_color = COLORS[option_index-4]
                    bulb.styles.background = Color.parse(f"{self.recent_color}{self.recent_alpha}")


class CommandHistory(Static):
    message_history = []

    def compose(self) -> ComposeResult:
        yield Log()

    def write_command(self, command:str) -> None:
        log = self.query_one(Log)
        self.message_history.append(command)
        log.write(f"{command}\n")


class GridLayout(App):
    CSS_PATH = "ui.tcss"
    BINDINGS = [("q", "quit", "Exit Application")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select.from_values(OPTIONS)
        yield LightBulbStatus()
        yield CommandHistory()
        yield Static("", classes="empty")
        yield Footer()

    def on_mount(self) -> None:
        # Adding titles to frames
        self.title = "Lightbulb Controller"
        #        self.sub_title = "sub title"
        ## Command selector
        self.query_one(Select).prompt = "Please select a command"
        ## history
        self.query_one(CommandHistory).border_title = "Command History"

    
    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        match event.value:
            case Select.BLANK:
                pass
            case _:
                history = self.query_one(CommandHistory)
                history.write_command(str(event.value))
                self.query_one(Select).clear()
                bulb = self.query_one(LightBulbStatus)
                bulb.update_status(str(event.value))

if __name__ == "__main__":
    app = GridLayout()
    app.run()

