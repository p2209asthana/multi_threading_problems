import threading

class ReadWriteLock:
    def __init__(self):
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0

    def acquire_read(self):
        with self._read_ready:
            self._readers+=1

    def release_read(self):
        with self._read_ready: 
            self._readers-=1
            if self._readers == 0:
                self._read_ready.notifyAll()

    def acquire_write(self):
        #Acquire lock but don't proceed until there are no readers
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
         self._read_ready.release()

    # Context managers for external use
    class ReadContext:
        def __init__(self, lock):
            self.lock = lock
        
        def __enter__(self):
            self.lock.acquire_read()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.lock.release_read()
    
    class WriteContext:
        def __init__(self, lock):
            self.lock = lock
        
        def __enter__(self):
            self.lock.acquire_write()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.lock.release_write()
    
    def read_lock(self):
        """Return a context manager for read operations."""
        return self.ReadContext(self)
    
    def write_lock(self):
        """Return a context manager for write operations."""
        return self.WriteContext(self)



class Node:
    def __init__(self, key = None, value=None):
        self.key = key 
        self.value = value 
        self.next = None
        self.prev = None

# A threadsafe cache implementation which manages read /write locks separately
# read lock can be acquired by any number of threads
# write lock can be acquired by only one thread, and that too
# when there are no reader locks
class LRUCache:
    def __init__(self, capacity):
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.capacity = capacity
        self.size = 0
        self.nodeMap = {}
        self.lock = ReadWriteLock()

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node 
        self.head.next = node

    def _move_to_front(self, node):
        if node.prev == self.head:
            return
        prevNode = node.prev
        nextNode = node.next
        prevNode.next = nextNode
        nextNode.prev = prevNode
        self._add_to_front(node)

    def _del_last_node(self):
        delNode = self.tail.prev
        delNode.prev.next = self.tail
        self.tail.prev = delNode.prev
        delNode.prev = None
        delNode.next = None
        return delNode
        
    def put(self, key, value):
        with self.lock.write_lock():
            if key in self.nodeMap:
                node = self.nodeMap[key]
                node.value = value
                self._move_to_front(node)
            else:
                node = Node(key, value)
                self._add_to_front(node)
                self.nodeMap[key] = node
                self.size+=1
    
            if self.size > self.capacity:
                delNode = self._del_last_node()
                del self.nodeMap[delNode.key]
                del delNode
                self.size-=1
            

    def get(self, key):
        with self.lock.read_lock():
            if key not in self.nodeMap:
                return -1
            node = self.nodeMap[key]
        with self.lock.write_lock():
            self._move_to_front(node)
            return node.value