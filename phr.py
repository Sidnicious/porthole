#!/usr/bin/env python2.7
import socket, pybonjour, select, json, os, sys

def get_computer_name():
    try:
        import subprocess
        return subprocess.check_output(['scutil', '--get', 'ComputerName'])[:-1]
    except:
        import socket
        return socket.gethostname()

class PortholeReceiver(object):

    def __init__(self, out):
        self.out = out
        pass

    def listen(self):
        listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_sock.bind(('', 0))
        listening_sock.listen(5)

        addr = listening_sock.getsockname()

        print "Listening on port {0}".format(addr[1])
        print "Your code is {0:02x}{1:02x}{2:02x}{3:02x}{4:04x}".format(69,200,239,41, addr[1])

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
                    # basename = os.path.basename(offer["name"])
                    # choice = raw_input("Hey, do you want this {0}-byte?\n[y] ".format(offer["size"], basename))
                    choice = None
                    if not choice or choice.lower() in set(('y', 'yes')):
                        while True:
                            d = connf.read(4096)
                            if not d: break
                            self.out.write(d)
                    break
        except KeyboardInterrupt:
            pass
        finally:
            sdRef.close()


if __name__ == '__main__':
    out = sys.stdout
    if not os.isatty(out.fileno()):
        out = os.fdopen(os.dup(out.fileno()), 'wb')
        tty = open('/dev/tty', 'wb')
        os.dup2(tty.fileno(), sys.stdout.fileno())

    PortholeReceiver(out).listen()
