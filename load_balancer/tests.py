
# Test the corrected implementation
def test_corrected_load_balancer():
    print("=== Testing Corrected Load Balancer ===\n")
    
    # Initialize
    servers = ["server1", "server2", "server3"]
    lb = ThreadSafeLoadBalancer(servers)
    
    # Test Round Robin
    print("=== Round Robin Test ===")
    for i in range(6):
        server = lb.get_server("round_robin")
        print(f"Request {i+1}: {server}")
    
    # Test Least Connections
    print("\n=== Least Connections Test ===")
    lb.record_connection("server1")
    lb.record_connection("server1")
    lb.record_connection("server2")
    
    print("Server stats:", lb.get_server_stats())
    
    for i in range(3):
        server = lb.get_server("least_connections")
        print(f"Request {i+1}: {server}")
    
    # Test server management
    print("\n=== Server Management Test ===")
    print(f"Initial servers: {lb.servers_list}")
    
    lb.add_server("server4")
    print(f"After adding server4: {lb.servers_list}")
    
    removed = lb.remove_server("server2")
    print(f"Removed server2: {removed}")
    print(f"Servers after removal: {lb.servers_list}")
    
    # Test health checking
    print("\n=== Health Check Test ===")
    lb.set_server_healthy("server1", False)
    print(f"Healthy servers: {lb.get_healthy_servers()}")
    
    print("Least connections with server1 unhealthy:")
    for i in range(3):
        server = lb.get_server("least_connections")
        print(f"Request {i+1}: {server}")


if __name__ == "__main__":
    test_corrected_load_balancer()