import socket
import global_settings

SERVER = "127.0.0.1"
PORT = 8080
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("HELLO list_client_features", global_settings.STANDARD_ENCODING))
print("From Client : HELLO list_client_features")

in_data = client.recv(1024)
print("From Server :", in_data.decode())
out_data = "LIST_GAMES"
print("Client send :", out_data)
client.sendall(bytes(out_data, global_settings.STANDARD_ENCODING))

in_data = client.recv(1024)
print("From Server :", in_data.decode())
out_data = "CREATE_MATCH Pong testmatch1"
print("Client send :", out_data)
client.sendall(bytes(out_data, global_settings.STANDARD_ENCODING))

in_data = client.recv(1024)
print("From Server :", in_data.decode())
out_data = "LIST_MATCHES Pong "
print("Client send :", out_data)
client.sendall(bytes(out_data, global_settings.STANDARD_ENCODING))


in_data = client.recv(1024)
print("From Server :", in_data.decode())
out_data = "JOIN_MATCH testmatch1 117,112,179"
print("Client send :", out_data)
client.sendall(bytes(out_data, global_settings.STANDARD_ENCODING))

while True:
    in_data = client.recv(1024)
    print("From Server :", in_data.decode())
    #out_data = input()
    #if out_data == "":
    #    out_data = "HELLO myname listofmafeatures"
    #client.sendall(bytes(out_data, global_settings.STANDARD_ENCODING))
    #if out_data == 'bye':
    #   pass
client.close()
