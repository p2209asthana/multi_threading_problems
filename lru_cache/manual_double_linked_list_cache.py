import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random


class Node:
    """Node for doubly linked list."""
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None


class ManualLRUCache:
    """
    Thread-safe LRU Cache with manual doubly linked list implementation.
    Provides more control over the data structure operations.
    """
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache: Dict[int, Node] = {}
        self.lock = Lock()  # Regular lock is sufficient
        
        # Create dummy head and tail nodes
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node: Node) -> None:
        """Add node right after head."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: Node) -> None:
        """Remove node from linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _move_to_head(self, node: Node) -> None:
        """Move node to head (most recently used)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def _remove_tail(self) -> Node:
        """Remove and return last node before tail."""
        last_node = self.tail.prev
        self._remove_node(last_node)
        return last_node
    
    def get(self, key: int) -> int:
        """Get value by key. Returns -1 if key doesn't exist."""
        with self.lock:
            if key not in self.cache:
                return -1
            
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
    
    def put(self, key: int, value: int) -> None:
        """Put key-value pair. Evicts LRU item if capacity exceeded."""
        with self.lock:
            if key in self.cache:
                # Update existing node
                node = self.cache[key]
                node.value = value
                self._move_to_head(node)
            else:
                # Add new node
                new_node = Node(key, value)
                
                if len(self.cache) >= self.capacity:
                    # Remove LRU node
                    tail_node = self._remove_tail()
                    del self.cache[tail_node.key]
                
                self.cache[key] = new_node
                self._add_to_head(new_node)
    
    def get_all(self) -> Dict[int, int]:
        """Get snapshot of all key-value pairs."""
        with self.lock:
            return {key: node.value for key, node in self.cache.items()}