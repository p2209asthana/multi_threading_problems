# **LeetCode-Style Problem: Thread-Safe Load Balancer**

## **Problem Statement**

Design a **thread-safe load balancer** that distributes incoming requests across multiple backend servers using different balancing algorithms.

Implement the `ThreadSafeLoadBalancer` class:

- `ThreadSafeLoadBalancer(List<String> servers)` Initialize the load balancer with a list of backend server URLs.
- `String getServer(String algorithm)` Return the next server to handle a request based on the specified algorithm. Supported algorithms:
 - `"round_robin"` - Distribute requests in circular order
 - `"least_connections"` - Route to server with fewest active connections
 - `"weighted_round_robin"` - Distribute based on server weights (assume equal weights initially)
- `void addServer(String server)` Add a new server to the pool. The server should immediately be available for routing.
- `boolean removeServer(String server)` Remove a server from the pool. Return `true` if server was removed, `false` if not found. Active connections should be allowed to complete.
- `void recordConnection(String server)` Record that a new connection was established to the specified server.
- `void recordDisconnection(String server)` Record that a connection to the specified server was closed.
- `void setServerWeight(String server, int weight)` Set the weight for weighted round robin algorithm. Default weight is 1.
- `Map<String, Integer> getServerStats()` Return current connection count for all servers.

**All operations must be thread-safe and support concurrent access from multiple threads.**

---

## **Constraints:**
- `1 <= servers.length <= 100`
- `1 <= server.length <= 50`
- Server URLs are unique and non-empty strings
- `1 <= weight <= 100`
- At most `10^6` calls will be made to all methods combined
- **Multiple threads may call any method concurrently**

---

## **Example:**

```python
# Example 1:
servers = ["server1", "server2", "server3"]
lb = ThreadSafeLoadBalancer(servers)

# Thread 1:
server1 = lb.getServer("round_robin")  # returns "server1"
server2 = lb.getServer("round_robin")  # returns "server2"

# Thread 2 (concurrent):
server3 = lb.getServer("round_robin")  # returns "server3"
server4 = lb.getServer("round_robin")  # returns "server1" (wrapped around)

# Thread 1 (concurrent):
lb.recordConnection("server1")
lb.recordConnection("server1")
lb.recordConnection("server2")

# Thread 3 (concurrent):
server5 = lb.getServer("least_connections")  # returns "server3" (0 connections)
lb.recordConnection("server3")

# Thread 2 (concurrent):
stats = lb.getServerStats()  # returns {"server1": 2, "server2": 1, "server3": 1}

# Thread 1 (concurrent):
lb.addServer("server4")
server6 = lb.getServer("round_robin")  # returns "server2" (continues from where it left off)