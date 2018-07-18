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

    (host, port) = load.load_server_data("serverinfo", "dat")

    s = ssh.init_socket(host, port, 5)

    ssh.set_server_name("Broker")

    servers = dict()

    while True:
        conn, addr = s.accept()
        clnthndlr = ssh.generate_client_handler(host=host, port=port, client_name="Test Server", conn=conn, addr=addr, call_back=_handle_client, call_back_args=(servers, ))
        clnthndlr.handle_connection()

    s.close()
