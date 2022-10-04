""" should make a server_functions which is able to communicate with multiple clients at once by multithreading.

LOBBY:
general:
    - TCP client/server model
    - Each message is terminated by null Byte (\x00)
    - There is a limit of 1024*1024 Bytes (1 MB) per TCP message.
    - All text has to be encoded in ASCII, if not otherwise stated.
      Mixed encodings are allowed for custom features.
    - All text is only allowed to contain the characters A-Za-z0-9_.!
    - Lists (denoted as list<> in the protocol description) are always
      comma-separated and are not allowed to contain spaces.
    - Colors are always denoted as a list representing a decimal RGB code.
server specification:
    - The server shall support one lobby and multiple active matches.
    - One client can only be part of one match.
    - If a match in the lobby has no active players anymore, it is deleted.
extensions/features:
    - The protocol can be extended or modified through features.
    - The available features are negotiated during the handshake between server and client.
    - All protocol details, except the handshake, can be modified by a feature.

more: https://gitlab.lrz.de/LKN_IK_Games/GameProtocol/-/blob/master/lobby/README.md
"""
""" should make a server which is able to communicate with multiple clients at once by multithreading. """

from server_functions.lobby import LobbyClass

if __name__ == "__main__":
    lobby = LobbyClass()
    lobby.run()
