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

# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

server_port = 12000

# Define the client class which will be used to store information about each client that connects
class Client:
  def __init__(self, address, socket):
    self.address = address
    self.socket = socket
    self.send_buffer = []
    self.receive_buffer = []
    self.connected = True
    
	# If this isn't the first client, set the receive buffer of both clients to the other's send buffer
    if (len(clients) > 0):
      for x in clients:
        if x != self:
          self.receive_buffer = x.send_buffer
          x.receive_buffer = self.send_buffer
          # Also set the appropriate name based on connection order
          self.name = "Client Y" if x.name == "Client X" else "Client X"
    else: self.name = "Client X"
		
def connection_handler(client):
  # Read data from the new connection socket
  # Note: if no data has been sent this blocks until there is data

  while True:
    query = client.socket.recv(1024)

    # Decode data from UTF-8 bytestream
    query_decoded = query.decode()

	# Client has disconnected - exit this thread's loop
    if not query or query_decoded == "bye":
      break

    # Log query information
    log.info("Received query test \"" + str(query_decoded) + "\"")
    # Append client name to message
    response = client.name + ": " + query_decoded
    
    # Add response to buffer
    client.receive_buffer.append(response)
    
    # Show response and receive buffer for troubleshooting only
    print("Response:", response)
    print(client.receive_buffer)
  
  # Client has now said bye. Remove it from client list
  clients.remove(client)
  # Close client socket
  client.socket.close()
  # Tell any other active clients that the client has left
  for x in clients:
    x.socket.send("{} has left the chat.".format(client.name).encode())

def broadcast_loop():
  # Send any pending messages
  while True:
    for client in clients:
      if len(client.send_buffer) > 0:
        try:
          client.socket.send(client.send_buffer.pop(0).encode())
          print("Response sent")
        except OSError as e:
          log.info("Client socket no longer open")
    time.sleep(0.5)
  

def main():
  # Create a TCP socket
  # Notice the use of SOCK_STREAM for TCP packets
  server_socket = s.socket(s.AF_INET,s.SOCK_STREAM)
  
  # Assign port number to socket, and bind to chosen port
  server_socket.bind(('',server_port))
  
  # Configure how many requests can be queued on the server at once
  server_socket.listen(1)
  
  # Alert user we are now online
  log.info("The server is ready to receive on port " + str(server_port))
  

  # Start a thread to handle sending messages, because each client-specific thread will block as it waits for client input
  _thread.start_new_thread(broadcast_loop, ())
  
  # Surround with a try-finally to ensure we clean up the socket after we're done
  try:
    # Enter forever loop to listen for requests
    while True:
      # When a client connects, create a new socket and record their address
      connection_socket, address = server_socket.accept()
      new_client = Client(address, connection_socket)
      log.info("Connected to {} at {}".format(new_client.name, str(address)))
      clients.append(new_client)
      
      # Pass the new socket and address off to a connection handler function in a new thread
      _thread.start_new_thread(connection_handler, (new_client,))


  finally:
    server_socket.close()

if __name__ == "__main__":
  main()
