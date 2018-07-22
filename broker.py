import time

import load
import registration_manager as rm
import server_reception_manager as srm
import server_socket_handler as ssh
from log import log

PACKET_ID_REGISTER = 100
PACKET_ID_STATUS = 101
PACKET_ID_REQUEST_SERVER_INFO = 102


def _handle_client(clnthndlr, servers):
    clnthndlr.print_connection_info()

    rgstrtnmngr = rm.RegistrationManager(servers)
    rcptnmngr = srm.ReceptionManager(clnthndlr, [rgstrtnmngr])

    rcptnmngr.init()
    rgstrtnmngr.init()

    delay = 1

    try:
        while clnthndlr.isConnected:
            start = time.time()

            rcptnmngr.loop()
            rgstrtnmngr.loop(clnthndlr)

            clnthndlr.send_all()

            end = time.time()
            diff = end - start

            if diff < delay:
                time.sleep(delay - diff)
    except Exception as e:
        if str(e) != "[WinError 10054] An existing connection was forcibly closed by the remote host":
            log(e)
        clnthndlr.isConnected = False

    finally:
        clnthndlr.print_disconnection_info()
        clnthndlr.disconnect()


if __name__ == "__main__":

    log("Server Started!\n")

    (broker_ip, broker_port) = load.load_server_data("serverinfo", "dat")

    s = ssh.init_socket(broker_ip, broker_port, 5)

    servers = dict()

    connCount = 0

    while True:
        conn, addr = s.accept()
        clnthndlr = ssh.generate_handler(self_name="Broker", peer_name="Client " + str(connCount), conn=conn, self_ip=broker_ip, self_port=broker_port, peer_ip=addr[0], peer_port=addr[1], call_back=_handle_client, call_back_args=(servers, ))
        clnthndlr.handle_connection()
        connCount += 1

    s.close()
