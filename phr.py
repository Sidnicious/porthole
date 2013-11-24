#!/usr/bin/env python2.7
import socket, pybonjour, select, json, os

def get_computer_name():
    try:
        import subprocess
        return subprocess.check_output(['scutil', '--get', 'ComputerName'])[:-1]
    except:
        import socket
        return socket.gethostname()

class PortholeReceiver(object):

    def __init__(self):
        pass

    def listen(self):
        listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_sock.bind(('', 0))
        listening_sock.listen(5)

        addr = listening_sock.getsockname()

        sdRef = pybonjour.DNSServiceRegister(
            name=get_computer_name(), regtype='_porthole._tcp', port=addr[1]
        )

        try:
            while True:
                ready = select.select([sdRef, listening_sock], [], [])
                if sdRef in ready[0]:
                    pybonjour.DNSServiceProcessResult(sdRef)
                if listening_sock in ready[0]:
                    conn, addr = listening_sock.accept()
                    connf = conn.makefile()
                    offer = json.loads(connf.readline())
                    basename = os.path.basename(offer["name"])
                    choice = raw_input("Hey, do you want this {0}-byte file called {1}?\n[y] ".format(offer["size"], basename))
                    if not choice or choice.lower() in set(('y', 'yes')):
                        out = open(basename, 'wb')
                        while True:
                            d = connf.read(4096)
                            if not d: break
                            out.write(d)
                    break
        except KeyboardInterrupt:
            pass
        finally:
            sdRef.close()


if __name__ == '__main__':
    PortholeReceiver().listen()
