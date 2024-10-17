#!env python

"""Chat server for CST311 Programming Assignment 3"""
__author__ = "Team 2"
__credits__ = [
  "Henry Garkanian",
  "Ivan Soria",
  "Kyle Stefun",
  "Bryan Zanoli"
]

import socket as s
import time
import _thread

clients = []
pending_messages = []

# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

server_port = 12000

# Defined class that inhibits every trait used in the socket buffer.
class Client:
  def __init__(self, address, socket):
    self.name = ""
    self.address = address
    self.socket = socket
    self.send_buffer = []
    self.receive_buffer = []
    self.connected = True
    
	# If this isn't the first client, set the receive buffer of both clients to the other's send buffer.
    if (len(clients) > 0):
      for x in clients:
        if x != self:
          self.receive_buffer = x.send_buffer
          x.receive_buffer = self.send_buffer
		
def connection_handler(client):
  # Reads data from the new connection socket.
  # Note: if no data has been sent, this blocks until there is data available.
  
  # Ask for client username.
  client_name = client.socket.recv(1024)
  
  #Set client username to provided value.
  client.name = client_name.decode()
  log.info("Connected to {} at {}".format(client.name, str(client.address)))
  
  # Send client its username as confirmation.
  client.socket.send(client.name.encode())
  clients.append(client)

  # Put any pending messages into the send buffer.
  while len(pending_messages) > 0:
    client.send_buffer.append(pending_messages.pop(0))

  while True:
    # Receive message from client
    query = client.socket.recv(1024)

    # Decode data from UTF-8 bytestream.
    query_decoded = query.decode()

	# Client has disconnected - exit this thread's loop.
    if not query or query_decoded == "bye":
      break

    # Append client name to message and insert null terminator to avoid clientside concatenation of multiple messages.
    response = client.name + ": " + query_decoded + "\0"
    
    # If only one client is connected, save this message for later.
    if len(clients) == 1:
      pending_messages.append(response)
    # Otherwise, put it in the message buffer to be sent in the broadcast loop.
    else:
      client.receive_buffer.append(response)
  
  # Client has disconnected. Remove it from client list.
  clients.remove(client)
  # Close client socket
  client.socket.close()
  # Tell any other active clients that the client has left.
  for x in clients:
    x.socket.send("{} has left the chat.".format(client.name).encode())

def broadcast_loop():
  # Send any messages that are pending.
  while True:
    for client in clients:
      if len(client.send_buffer) > 0:
        try:
          while len(client.send_buffer) > 0:
            client.socket.send(client.send_buffer.pop(0).encode())
        except OSError as e:
          log.info("Client socket no longer open")
    time.sleep(0.2)
  

def main():
  # Create a TCP socket.
  # Notice the use of SOCK_STREAM for TCP packets.
  server_socket = s.socket(s.AF_INET,s.SOCK_STREAM)
  
  # Assign port number to socket, and bind to chosen port.
  server_socket.bind(('',server_port))
  
  # Configure how many requests can be queued on the server at once.
  server_socket.listen(1)
  
  # Alert user we are now online.
  log.info("The server is ready to receive on port " + str(server_port))
  

  # Start a thread to handle sending messages, 
  # because each client-specific thread will block as it waits for client input.
  _thread.start_new_thread(broadcast_loop, ())
  
  # Surround with a try-finally to ensure we clean up the socket after we're done.
  try:
    # Enter infinite while loop to listen for requests.
    while True:
      # When a client connects, create a new socket and record their address.
      connection_socket, address = server_socket.accept()
      new_client = Client(address, connection_socket)
      
      # Pass the new socket and address off to a connection handler function in a new thread.
      _thread.start_new_thread(connection_handler, (new_client,))
      
  finally:
    server_socket.close()

if __name__ == "__main__":
  main()
