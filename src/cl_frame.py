import struct
import socket
import hashlib
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
	def connframe(self, lo_addr, hashcode):
		bytes = struct.pack("H", 400)
		bytes += self.addr2bytes(lo_addr)
		bytes += struct.pack("40s", str(hashcode))
		return bytes

	def loginframe(self, hashcode):
		bytes = struct.pack("H", 200)
		bytes += struct.pack("40s", str(hashcode))
		return bytes

	def recvpeer(self, frame):
		lo_addr = self.bytes2addr(frame[2:8])
		public = self.bytes2addr(frame[8:14])
		target = self.bytes2addr(frame[14:20])		
		hashcode, = struct.unpack("40s", frame[20:])
		return hashcode, lo_addr, public, target

	def recvres(self, frame):
		try:			
			res, = struct.unpack("H", frame[:2])
			return res
		except Exception:
			return
	def recvhash(self, frame):
		hashcode, = struct.unpack("40s", frame[2:])
		return hashcode
