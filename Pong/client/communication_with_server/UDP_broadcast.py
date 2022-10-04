import socket
import global_settings


def server_discovery():
    """
    send broadcast message to find out which IP and port the server has
    """
    server_port = 54000
    print(f"sending broadcast message to Port {server_port}")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dst_udp = (global_settings.SERVER_IP_ADDR, server_port)  # TODO make this a real broadcast
    message = "DISCOVER_LOBBY\0".encode(global_settings.STANDARD_ENCODING)
    udp_sock.sendto(message, dst_udp)
    print("sent discovery")

    # receiving and checking the udp answer from the server
    byte_udp_answer, address = udp_sock.recvfrom(54006)
    udp_answer = byte_udp_answer.decode("ASCII")
    udp_answer_nullbyte = udp_answer.split("\0")
    print(f"server answer: {udp_answer}")
    udp_answer_list = udp_answer_nullbyte[0].split(" ")
    print(udp_answer_list)
    if udp_answer_list[0] == "LOBBY":
        # ip is the same as in the udp connection, only the port is different for tcp
        tcp_address = (address[0], int(udp_answer_list[1]))
        return tcp_address
    else:
        udp_sock.sendto("ERR_CMD_NOT_UNDERSTOOD".encode("ASCII"), dst_udp)

    udp_sock.close()