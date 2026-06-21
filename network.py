import asyncio
import json
import socket

class LocalDataMesh:
    def __init__(self, host='127.0.0.1', port=7777):
        self.host = host
        self.port = port
        self.connected_nodes = set()

    async def handle_node(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[MESH] New node connection established from: {addr}")
        self.connected_nodes.add(writer)

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                # Parse incoming data stream packet
                packet = json.loads(data.decode())
                print(f"[MESH] Data Packet Received from {addr}: {packet}")
                
                # Broadcast processing loop to all other active layers
                await self.broadcast(data, exclude=writer)
        except Exception as e:
            print(f"[MESH] Error or disconnection at {addr}: {e}")
        finally:
            self.connected_nodes.remove(writer)
            writer.close()
            await writer.wait_closed()
            print(f"[MESH] Connection closed for node: {addr}")

    async def broadcast(self, data, exclude=None):
        for node in self.connected_nodes:
            if node != exclude:
                try:
                    node.write(data)
                    await node.drain()
                except Exception:
                    pass

    async def start(self):
        server = await asyncio.start_server(self.handle_node, self.host, self.port)
        print(f"[STATUS] Omni Data Mesh Engine active offline at {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    mesh = LocalDataMesh()
    try:
        asyncio.run(mesh.start())
    except KeyboardInterrupt:
        print("\n[STATUS] Data Mesh Engine cleanly terminated.")