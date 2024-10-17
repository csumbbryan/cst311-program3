#!env python

"""Chat client for CST311 Programming Assignment 3"""
__author__ = "Team 2"
__credits__ = [
  "Henry Garkanian",
  "Ivan Soria",
  "Kyle Stefun",
  "Bryan Zanoli"
]

# Import statements.
import socket as s
import _thread
import threading
import time

# Configure logging.
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set global variables.
server_name = "10.0.0.1"
server_port = 12000
complete = 0

def client_input(client_socket):
    try:
        # Get input from user
        while True: 
            user_input = input()
            # Set data across socket to server.
            # Note: encode() converts the string to UTF-8 for transmission.
            client_socket.send(user_input.encode())
            if (user_input == 'bye'):
                complete = 1
                break
    finally:
        print()

def client_receive(client_socket):
    try:
        while True:  
            # Read response from server.
            server_response = client_socket.recv(1024)
            # Decode server response from UTF-8 bytestream.
            server_response_decoded = server_response.decode()
            # Print output from server - split on null character to avoid concatenation.
            split_response = server_response_decoded.strip('\0').split('\0')
            for x in split_response:
              print(x)
            
    except OSError as e:
        log.info("Client socket no longer open")
    finally:
        print()
        
def input_clientname(client_socket):
    print("Welcome to the chat! Please enter your username:")
    user_input = input()
    
    # Send client name to server.
    client_socket.send(user_input.encode())
    # Get server response.
    server_response = client_socket.recv(1024)
    # If returned name from server does not match, log an error.
    if(user_input != server_response.decode()):
        log.error("username could not be set")
    

def main():
    # Create socket.
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)

    try:
        # Establish TCP connection.
        client_socket.connect((server_name,server_port))
    # Log error if client socket cannot be established
    except Exception as e:
        log.exception(e)
        log.error("***Advice:***")
        if isinstance(e, s.gaierror):
            log.error("\tCheck that server_name and server_port are set correctly.")
        elif isinstance(e, ConnectionRefusedError):
            log.error("\tCheck that server is running and the address is correct")
        else:
            log.error("\tNo specific advice, please contact teaching staff and include text of error and code.")
        exit(8)
    
    #Call function to collect and set client name
    input_clientname(client_socket)
    # Start separate threads for client input (send) and client receive to 
    #ensure bidirectional communication
    _thread.start_new_thread(client_input, (client_socket,))
    _thread.start_new_thread(client_receive, (client_socket,))
    
    #Wait for client to finish, then close the socket
    while True:
        if (complete == 1):
            break
        time.sleep(.5)
    client_socket.close()

# This helps shield code from running when we import the module.
if __name__ == "__main__":
    main()
