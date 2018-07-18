from log import log


def load_server_data(file_name, file_ext):
    file = open(file_name + '.' + file_ext)

    host = ''
    port = 1
    next = file.readline()

    while next != '':
        next = next.strip()
        if next[:5] == "host:":
            host = next[5:]
        elif next[:5] == "port:":
            port = int(next[5:])
        else:
            log("Error: invalid server information!!!")
        next = file.readline()
    file.close()

    return host, port
