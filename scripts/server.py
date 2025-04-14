import os
import socket
import threading

# Existing imports
from utils import recv_msg
from server_backend import get_arg_parser, recv_next_command
from authentication import authenticate

os.chdir(os.path.dirname(os.path.realpath(__file__)))  # move path to file directory
 
# Function to handle each client connection
def handle_client(conn, addr, args):
    """
    Process a single client connection in its own thread
    """
    print(f'Connected by {addr}')
    try:
        client_args = recv_next_command(conn)
        
        if client_args['auth']:
            client_key = authenticate(client_args, is_client=False, conn=conn)
            if client_key == False:
                print(f'Authentication failed for {addr}, closing connection')
                return
            else:
                print(f'Successfully authenticated client {addr}')
                # Continue with next command
                client_args = recv_next_command(conn)

        # Process the client's function request
        result = client_args['function'](conn, client_args)

        final_client_resp = recv_msg(conn)
        if final_client_resp in [b'200']:
            print(f"Transaction with {addr} completed successfully")
        else:
            print(f"WARNING: transaction with {addr} didn't complete successfully: client didn't send TRANSACTION_COMPLETED (200)")
    
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    
    finally:
        print(f"Closing connection with {addr}")
        conn.close()

if __name__ == "__main__":
    print("COE451 ProgAssignment1: SFTP client-server."
          "\nServer side" +
          "\n=======================================")
    parser = get_arg_parser()
    args = vars(parser.parse_args())

    # Create a server socket that will listen for connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Enable socket address reuse
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind((args['host'], args['port']))
        s.listen(5)  # Allow up to 5 connections to queue
        
        print(f"Server started on {args['host']}:{args['port']}, waiting for connections...")
        
        try:
            while True:
                conn, addr = s.accept()
                # Create a new thread to handle the client
                client_thread = threading.Thread(target=handle_client, args=(conn, addr, args))
                client_thread.daemon = True  # Make thread exit when main program exits
                client_thread.start()
                print(f"Active connections: {threading.active_count() - 1}")
        
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        except Exception as e:
            print(f"Error: {e}")
