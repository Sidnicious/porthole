#!/usr/bin/env python2.7
# coding=utf-8
import sys, pybonjour, select, json, socket, os

class scanner(object):

	def __init__(self):
		self.services = {}

		def on_browse(
			sdRef, flags, interfaceIndex, errorCode, serviceName,
			regtype, replyDomain
		):
			if not (flags & pybonjour.kDNSServiceFlagsAdd):
				if serviceName in self.services:
					del self.services[serviceName]
				return

			def on_resolve(
				sdRef, flags, interfaceIndex, errorCode, fullname,
				hosttarget, port, txtRecord
			):
				self.services[serviceName] = (hosttarget, port)

			pybonjour.DNSServiceProcessResult(
				pybonjour.DNSServiceResolve(
					0, interfaceIndex, serviceName, regtype, replyDomain,
					on_resolve
			))

		self.browse_sdRef = pybonjour.DNSServiceBrowse(
			regtype='_porthole._tcp', callBack=on_browse
		)

	def scan(self):
		try:
			select.select([self.browse_sdRef], [], [])
		except KeyboardInterrupt:
			return
		pybonjour.DNSServiceProcessResult(self.browse_sdRef)

def send(filename, client):
	with open(filename, 'rb') as f:
		f.seek(0, 2)
		size = f.tell()
		f.seek(0)

		sock = socket.socket()
		sock.connect(client)
		sock.send(json.dumps({ "type": "offer", "name": os.path.basename(filename), "size": size }))
		sock.send('\n')
		while True:
			d = f.read(4096)
			if not d: break
			sock.send(d)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.stderr.write('usage: {0} file\n'.format(sys.argv[0]))
		sys.exit(1)

	filename = sys.argv[1]
	s = scanner()

	print "Looking for receivers…"

	s.scan()

	service_list = []
	chosen_service = None

	if s.services:
		for service in s.services.items():
			print "[{0}] {1}".format(len(service_list), service[0])
			service_list.append(service[1])
		print

		try:
			choice = raw_input('Send to: ')
			chosen_service = service_list[int(choice)]
		except:
			pass

	if chosen_service:
		send(filename, chosen_service)
