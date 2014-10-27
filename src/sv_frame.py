import struct
import socket
class Frame(object):
	"""docstring for Frame"""
	def __init__(self):
		pass
	def bytes2addr(self, bytes):
		if len(bytes) != 6:
			raise (ValueError, "invalid bytes")
		host = socket.inet_ntoa( bytes[:4])
		port, = struct.unpack( "H", bytes[-2:])
		return (host, port)
	def addr2bytes(self, addr):
		host, port = addr
		try:
			host = socket.gethostbyname(host)
		except (socket.gaierror, socket.error):
			raise (ValueError, "invalid host")
		try:
			port = int(port)
		except ValueError:
			raise (ValueError, "invalid port")
		bytes  = socket.inet_aton( host )
		bytes += struct.pack( "H", port )
		return bytes

	def sendpeer(self, hashcode,local,public,target):
		bytes = struct.pack("H", 400)
		bytes += self.addr2bytes(local) + self.addr2bytes(public) + self.addr2bytes(target)		
		bytes += struct.pack("40s", str(hashcode))
		return bytes
	def sendbind(self, hashcode):
		bytes = struct.pack("H", 100)
		bytes += struct.pack("40s", str(hashcode))
		return bytes

	def recvreq(self, frame):
		try:
			req, = struct.unpack("H", frame[:2])
			return req
		except Exception:
			return	
	def reqconn(self, frame):
		local = self.bytes2addr(frame[2:8])
		hashcode, = struct.unpack("40s", frame[8:])
		return local, hashcode
	def recvhash(self, frame):
		unpacker = struct.Struct('H 40s')
		req, hashcode, = unpacker.unpack(frame)
		return hashcode