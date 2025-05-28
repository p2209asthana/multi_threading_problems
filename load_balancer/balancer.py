import threading
from typing import List, Dict, Optional

class Server:
    def __init__(self, name):
        self.name = name 
        self.connections = 0
        self.healthy = True
        self.lock = threading.Lock()  # Added for thread-safe connection updates
        
class RWLock:
    def __init__(self):
        self.readers = 0
        self.read_ready = threading.Condition(threading.RLock())

    def read_lock(self):
        return self.ReadLock(self)

    def write_lock(self):
        return self.WriteLock(self)
        
    class ReadLock:
        def __init__(self, lock):
            self.lock = lock

        def __enter__(self):
            self.acquire()

        def __exit__(self, a, b, c):  # Fixed: was missing underscore
            self.release()
    
        def acquire(self):
            self.lock.read_ready.acquire()
            try:
                self.lock.readers += 1
            finally:
                self.lock.read_ready.release()
                
        def release(self):
            self.lock.read_ready.acquire()
            try:
                self.lock.readers -= 1
                if self.lock.readers == 0:
                    self.lock.read_ready.notifyAll()
            finally:
                self.lock.read_ready.release()
                
    class WriteLock:
        def __init__(self, lock):
            self.lock = lock 

        def __enter__(self):
            self.acquire()

        def __exit__(self, a, b, c):  # Fixed: was missing underscore
            self.release()
        
        def acquire(self):
            self.lock.read_ready.acquire()
            while self.lock.readers > 0:
                self.lock.read_ready.wait()
    
        def release(self):
            self.lock.read_ready.release()
    
class ThreadSafeLoadBalancer:

    def __init__(self, servers):
        self.servers = {}
        self.servers_list = []  # Fixed: consistent naming
        for server in servers:
            self.servers[server] = Server(server)
            self.servers_list.append(server)

        self.rr_next_index = 0

        self.server_collection_lock = RWLock()
        self.rr_lock = threading.RLock()
        
    def get_server(self, algorithm):
        with self.server_collection_lock.read_lock():
            if not self.servers_list:
                return None
            if algorithm == "round_robin":  # Fixed: consistent naming
                return self._get_rr_server()
            elif algorithm == "least_connections":
                return self._get_lc_server()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
           
    def _get_rr_server(self):
        with self.rr_lock:
            server_idx = self.rr_next_index % len(self.servers_list)  # Fixed: use servers_list
            server = self.servers_list[server_idx]
            self.rr_next_index = (server_idx + 1) % len(self.servers_list)  # Fixed: increment properly
            return server

    def _get_lc_server(self):
        # Find server with least connections
        min_connections = float('inf')
        selected_server = None
        
        for server_name in self.servers_list:
            server = self.servers[server_name]
            if server.healthy:
                with server.lock:
                    if server.connections < min_connections:
                        min_connections = server.connections
                        selected_server = server_name
        
        # If no healthy server found, return first available
        if selected_server is None and self.servers_list:
            selected_server = self.servers_list[0]
            
                    return selected_server
        
    def add_server(self, server):
        with self.server_collection_lock.write_lock():  # Fixed: missing colon
            if server not in self.servers:
                self.servers[server] = Server(server)
                self.servers_list.append(server)

    def remove_server(self, server):
        with self.server_collection_lock.write_lock():  # Fixed: missing colon
            if server in self.servers:
                del self.servers[server]
                self.servers_list.remove(server)  # Fixed: use servers_list
                return True
            return False

    def record_connection(self, server):
        # Fixed: Use read lock since we're not modifying the collection structure
        # and add proper thread-safe connection increment
        server_obj = self.servers.get(server)
        if server_obj:
            with server_obj.lock:
                server_obj.connections += 1  # Fixed: was trying to increment dict

    def record_disconnection(self, server):
        # Fixed: Use read lock and proper thread-safe connection decrement
        server_obj = self.servers.get(server)
        if server_obj:
            with server_obj.lock:
                server_obj.connections = max(0, server_obj.connections - 1)  # Fixed: prevent negative

    def get_server_stats(self) -> Dict[str, int]:
        """Return current connection count for all servers."""
        stats = {}
        for server_name, server_obj in self.servers.items():
            with server_obj.lock:
                stats[server_name] = server_obj.connections
        return stats

    def set_server_healthy(self, server: str, healthy: bool):
        """Mark a server as healthy or unhealthy."""
        server_obj = self.servers.get(server)
        if server_obj:
            with server_obj.lock:
                server_obj.healthy = healthy

    def get_healthy_servers(self) -> List[str]:
        """Return list of currently healthy servers."""
        healthy_servers = []
        for server_name, server_obj in self.servers.items():
            if server_obj.healthy:
                healthy_servers.append(server_name)
        return healthy_servers