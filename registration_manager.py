import json

import broker
import manager
import packet
from log import log
import timer
import time

PING_DELAY = 180
PING_TIME_OUT = 5


class Server:
    def __init__(self, clnthndlr, server_handle, server_ip, server_port):
        self.clnthndlr = clnthndlr
        self.server_handle = server_handle
        self.server_ip = server_ip
        self.server_port = server_port
        self.status = None


class RegistrationManager(manager.Manager):

    def __init__(self, servers):
        self.servers = servers
        self.is_pinging = False
        self.timer = timer.Timer()

    def _add_server(self, clnthndlr, server_handle, server_ip, server_port):
        self.servers[server_handle] = Server(clnthndlr, server_handle, server_ip, server_port)
        log("\nServer registered w/: server_handle: %s, server_ip: %s, server_port: %s\n" % (server_handle, server_ip, server_port))

    def _get_server(self, server_handle):
        return self.servers[server_handle] if server_handle in self.servers else None

    def handle_ping(self, server_handle, server_status):
        self.is_pinging = False
        self.timer.reset()

        server = self._get_server(server_handle)
        server.status = server_status

        log("Status of %s is %s" % (server_handle, server_status))

    def handle_request(self, clnthndlr, packet_id, data):
        try:
            if packet_id is broker.PACKET_ID_REGISTER:
                data = json.loads(data.get_data())

                server_handle = data["data"]["server_handle"]
                server_ip = data["data"]["server_ip"]
                server_port = data["data"]["server_port"]

                self._add_server(clnthndlr, server_handle, server_ip, server_port)
            elif packet_id is broker.PACKET_ID_STATUS:
                data = json.loads(data.get_data())

                server_handle = data["data"]["server_handle"]
                server_status = data["data"]["server_status"]

                self.handle_ping(server_handle, server_status)
            elif packet_id is broker.PACKET_ID_REQUEST_SERVER_INFO:
                data = json.loads(data.get_data())

                server_handle = data["data"]["server_handle"]

                server = self._get_server(server_handle)

                if server:
                    server_ip = server.server_ip
                    server_port = server.server_port
                else:
                    server_ip = None
                    server_port = None

                pk = packet.Packet(json.dumps(dict(data=dict(server_handle=server_handle, server_ip=server_ip, server_port=server_port))), broker.PACKET_ID_REQUEST_SERVER_INFO)
                clnthndlr.send_packet(pk)

        except Exception as e:
            if not str(e) == "[WinError 10054] An existing connection was forcibly closed by the remote host":
                log(e)
                raise e
            clnthndlr.isConnected = False

    def init(self):
        pass

    def loop(self, clnthndlr):

        server = None

        for srv in self.servers:
            if self.servers[srv].clnthndlr == clnthndlr:
                server = self.servers[srv].clnthndlr
                break
        if not server:
            return

        if not self.is_pinging:
            if (time.time() // 1) % PING_DELAY == 0:
                pk = packet.Packet(json.dumps(dict(data="SEND_STATUS")), broker.PACKET_ID_STATUS)
                clnthndlr.send_packet(pk)
                self.is_pinging = True
                self.timer.reset()
                self.timer.start()
        else:
            self.timer.end()
            if self.timer.get() >= PING_TIME_OUT:
                clnthndlr.isConnected = False

    def responds_to(self, packet_id):
        return 100 <= packet_id < 200
