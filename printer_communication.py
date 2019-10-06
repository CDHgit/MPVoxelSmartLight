import socket
import requests
from time import sleep, gmtime, strftime
import json

with open("webhooks_urls.secret") as f:
    requests_dict = json.loads(f.read())

HOST = '192.168.1.200'  # IP address of MP Voxel 3D printer
PORT = 8899            # Port is 8899 by default
CMD_MESSAGE = bytes.fromhex("7e4d3131390d0a") # Request for status that includes machine state
BUFFER_SIZE = 1024
TIMEOUT = 1 # Timeout in seconds of the 3D Printer
REFRESH = 15 # Frequency in seconds of the check on the printer 

def check_printer_state():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(TIMEOUT)
        s.connect((HOST, PORT))
        s.send(CMD_MESSAGE)
        cmd_response = s.recv(BUFFER_SIZE)
        s.close()
    except socket.error as e:
        print("Failed to connect to socket, is the printer on? ERROR:", e)
        return False
    cmd_string = cmd_response.decode("utf-8") 
    response_fields = cmd_string.split("\r")
    machine_status = response_fields[2].split(':')[1].strip(' ')
    print(machine_status, strftime(" %Y-%m-%d %H:%M:%S", gmtime()))
    return machine_status == "BUILDING_FROM_SD"
    
    
def send_light_on_request():
    print("Turning ON the light in the 3D printing room ", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    requests.post(requests_dict["ON"])    

def send_light_off_request():
    print("Turning OFF the light in the 3D printing room ", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    requests.post(requests_dict["OFF"])   

if __name__ == "__main__":
    Printing_State = False
    Previous_Printing_State = False
    while(True):
        Printing_State = check_printer_state()
        if Printing_State is not Previous_Printing_State:
            Previous_Printing_State = Printing_State
            if Printing_State:
                send_light_on_request()
            else:
                send_light_off_request()
        sleep(REFRESH)
