import socket
import global_settings


SERVER = global_settings.LOCALHOST
PORT = global_settings.LOBBY_TCP_PORT

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client", 'UTF-8'))

while True:
    client.sendall(bytes("HELLO myfeatureslist", global_settings.STANDARD_ENCODING))
    in_data = client.recv(1024)
    print("From Server :", in_data.decode(global_settings.STANDARD_ENCODING))
    user_input = input("Press Enter to send Hello message again. Press Q and Enter to quit")
    if user_input == "Q" or user_input == "q":
        break
client.close()
