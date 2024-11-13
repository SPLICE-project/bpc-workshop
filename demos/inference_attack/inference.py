import subprocess
import socket
import base64

def command(cmd, message):
  output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
  print(message)
  send_packet(message)

def send_packet(message):
    host = ''
    port = 12345
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        dataLen = len(message)
        data = base64.b64encode(bytes(message, 'utf-8'))
        data = data * dataLen
        s.sendto(data, (host, port))

def process_command():
    commands = {
        "1": ["irsend SEND_ONCE lamp SWITCH_ON", "Turnedon"],
        "2": ["irsend SEND_ONCE lamp SWITCH_OFF", "Turnedoff"],
        "3": ["irsend SEND_ONCE lamp SWITCH_DIM", "Turneddim"],
        "4": ["irsend SEND_ONCE lamp SWITCH_BRIGHT", "Turnedbright"],
        "5": ["irsend SEND_ONCE lamp SWITCH_RED", "Turnedred"],
        "6": ["irsend SEND_ONCE lamp SWITCH_GREEN", "Turnedgreen"],
        "7": ["irsend SEND_ONCE lamp SWITCH_BLUE", "Turnedblue"],
        "8": ["irsend SEND_ONCE lamp SWITCH_WHITE", "Turnedwhite"],
        "9": ["irsend SEND_ONCE lamp SWITCH_ORANGE", "Turnedorange"],
        "10": ["irsend SEND_ONCE lamp SWITCH_SEAFOAM", "Turnedseafom"],
        "11": ["irsend SEND_ONCE lamp SWITCH_VIOLET", "Turnedviolet"],
        "12": ["irsend SEND_ONCE lamp SWITCH_YELLOW", "Turnedyellow"],
        "13": ["irsend SEND_ONCE lamp SWITCH_AQUA", "Turnedaqua"],
        "14": ["irsend SEND_ONCE lamp SWITCH_PURPLE", "Turnedpurple"],
        "15": ["irsend SEND_ONCE lamp SWITCH_LGREEN", "Turnedlightgreen"],
        "16": ["irsend SEND_ONCE lamp SWITCH_LBLUE", "Turnedlightblue"],
        "17": ["irsend SEND_ONCE lamp SWITCH_LPURPLE", "Turnedlightpurple"]
    }


    # Get user input
    user_input = input("Enter a command: ")

    # Process the input
    if user_input in commands:
        # Call the corresponding function
        cmd = commands[user_input][0]
        message = commands[user_input][1]
        command(cmd, message)
    elif user_input == 'q':
        print("Exiting...")
    elif user_input == 'c':
        display_commands()
    else:
        print("Invalid command. Please try again.")

    return user_input

def display_commands():
    # Display available commands
    print("Remote Controller: Available commands below:")
    print("1 - Switch On")
    print("2 - Switch Off")
    print("3 - Switch Dim")
    print("4 - Switch Bright")
    print("5 - Switch Red")
    print("6 - Switch Green")
    print("7 - Switch Blue")
    print("8 - Switch White")
    print("9 - Switch Orange")
    print("10 - Switch Seafoam")
    print("11 - Switch Violet")
    print("12 - Switch Yellow")
    print("13 - Switch Aqua")
    print("14 - Switch Purple")
    print("15 - Switch Light Green")
    print("16 - Switch Light Blue")
    print("17 - Switch Light Purple")
    print("c - Redisplay commands")
    print("q - Quit")

def main():
    display_commands()
    while True:
        user_input = process_command()
        if user_input == 'q':
            break

if __name__ == "__main__":
    main()
