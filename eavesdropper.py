import playground
import asyncio
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
# from playground.common import logging as p_logging
# p_logging.EnablePresetLogging(p_logging.PRESET_TEST)


class Demux(StackingProtocol):
	srclist=[]
	dstlist=[]

	def connectionMade(self):
		pass

	def demux(src, srcPort, dst, dstPort, demuxData):
		#if(not src in srclist):
#		print(src)
#		self.srclist.append(src)
		print("Packet from ", src, ":", srcPort, ". Going to ", dst, ":", dstPort)
#		print("srclist",self.srclist)
		# if(not dst in dstlist):
		# 	dstlist.append(src)
		print("Data: ", demuxData)


eavesdrop = playground.network.protocols.switching.PlaygroundSwitchTxProtocol(Demux, "20181.*.*.*")
coro = asyncio.get_event_loop().create_connection(lambda: eavesdrop, "192.168.200.240", 9090)
loop = asyncio.get_event_loop()
socket, client_proto = loop.run_until_complete(coro)
loop.run_forever()

