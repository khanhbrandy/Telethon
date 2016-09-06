# This file is based on TLSharp
# https://github.com/sochix/TLSharp/blob/master/TLSharp.Core/Network/TcpTransport.cs
from network import TcpMessage, TcpClient
from binascii import crc32
from errors import *


class TcpTransport:
    def __init__(self, ip_address, port):
        self._tcp_client = TcpClient()
        self._send_counter = 0

        self._tcp_client.connect(ip_address, port)

    def send(self, packet):
        """Sends the given packet (bytes array) to the connected peer"""
        if not self._tcp_client.connected:
            raise ConnectionError('Client not connected to server.')

        # Get a TcpMessage which contains the given packet
        tcp_message = TcpMessage(self._send_counter, packet)

        self._tcp_client.write(tcp_message.encode())
        self._send_counter += 1

    def receive(self):
        """Receives a TcpMessage from the connected peer"""

        # First read everything
        packet_length_bytes = self._tcp_client.read(4)
        packet_length = int.from_bytes(packet_length_bytes, byteorder='little')

        seq_bytes = self._tcp_client.read(4)
        seq = int.from_bytes(seq_bytes, byteorder='little')

        body = self._tcp_client.read(packet_length - 12)

        checksum = int.from_bytes(self._tcp_client.read(4), byteorder='little', signed=False)

        # Then perform the checks
        rv = packet_length_bytes + seq_bytes + body
        valid_checksum = crc32(rv)

        if checksum != valid_checksum:
            raise InvalidChecksumError(checksum, valid_checksum)

        # If we passed the tests, we can then return a valid TcpMessage
        return TcpMessage(seq, body)

    def close(self):
        if self._tcp_client.connected:
            self._tcp_client.close()
