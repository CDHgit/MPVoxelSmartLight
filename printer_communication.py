import socket
import requests
from time import sleep, gmtime, strftime
import json
import sys

# Import the webhooks urls from a json file so that they aren't included on github
with open("webhooks_urls.secret") as f:
    requests_dict = json.loads(f.read())

# If there are enough CLA the set the HOST and PORT from the command line
if len(sys.argv) > 1:
    HOST = sys.argv[1]  # IP address of MP Voxel 3D printer from CLA
else:
    HOST = '192.168.1.200'  # My IP address by default
if len(sys.argv) > 2:
    PORT = int(sys.argv[2]) # Port from CLA
else:
    PORT = 8899            # Port is 8899 by default

# Static values to be set once
CMD_MESSAGE = bytes.fromhex("7e4d3131390d0a") # Request for status that includes machine state
BUFFER_SIZE = 1024 # Overkill
TIMEOUT = 1 # Timeout in seconds of the 3D Printer
REFRESH = 15 # Frequency in seconds of the check on the printer 

# Creates a socket connecting to the printer, sends the command, parses the pritners resposne to give a boolean for printing
def check_printer_state():
    try:
        # Create the socket, connect, send the command, recv the response, close the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(TIMEOUT)
        s.connect((HOST, PORT))
        s.send(CMD_MESSAGE)
        cmd_response = s.recv(BUFFER_SIZE)
        s.close()
    except socket.error as e:
        # If the printer is not on or is already connected to another comptuer
        print("Failed to connect to socket, is the printer on? ERROR:", e)
        return False
    # Decode the hex response to text
    cmd_string = cmd_response.decode("utf-8")
    # Split by carriage returns and isoalte the machine status response
    response_fields = cmd_string.split("\r")
    machine_status = response_fields[2].split(':')[1].strip(' ')
    # Log the status
    print(machine_status, strftime(" %Y-%m-%d %H:%M:%S", gmtime()))
    # Return if the status means printing
    return machine_status == "BUILDING_FROM_SD"
    
    
def send_light_on_request():
    # Send the POST request to the webhooks ON URL
    print("Turning ON the light in the 3D printing room ", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    requests.post(requests_dict["ON"])    

def send_light_off_request():
    # Send the POST request to the webhooks OFF URL
    print("Turning OFF the light in the 3D printing room ", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    requests.post(requests_dict["OFF"])   

if __name__ == "__main__":
    # Assume as the initial state that the printer is off and has been off
    Printing_State = False
    Previous_Printing_State = False
    # Do this forever (use keyboard interrupt to exit ...)
    while(True):
        # Check on the printer
        Printing_State = check_printer_state()
        if Printing_State is not Previous_Printing_State:
            # If the status changed
            Previous_Printing_State = Printing_State
            if Printing_State:
                # From off to on, turn lights on
                send_light_on_request()
            else:
                # From on to off turn lights off
                send_light_off_request()
        # Wait for a bit because it isn't that serious
        sleep(REFRESH)
