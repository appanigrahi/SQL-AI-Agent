import socket

server = "SQL01"

try:
    ip = socket.gethostbyname(server)

    print({
        "server": server,
        "ip": ip,
        "dns_resolution": True
    })

except Exception as ex:
    print({
        "server": server,
        "dns_resolution": False,
        "error": str(ex)
    })