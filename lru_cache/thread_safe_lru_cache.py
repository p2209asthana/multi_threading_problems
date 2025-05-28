import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random

# ========== APPROACH 1: Basic Thread-Safe LRU Cache ==========
class ThreadSafeLRUCache:
    """
    Thread-safe LRU Cache using threading.RLock for synchronization.
    Uses OrderedDict for O(1) operations and automatic LRU ordering.
    """
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = Lock()  # Regular lock is sufficient - no recursive calls
    
    def get(self, key: int) -> int:
        """Get value by key. Returns -1 if key doesn't exist."""
        with self.lock:
            if key not in self.cache:
                return -1
            
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
    
    def put(self, key: int, value: int) -> None:
        """Put key-value pair. Evicts LRU item if capacity exceeded."""
        with self.lock:
            if key in self.cache:
                # Update existing key and move to end
                self.cache.pop(key)
                self.cache[key] = value
            else:
                # Add new key
                if len(self.cache) >= self.capacity:
                    # Remove least recently used (first item)
                    self.cache.popitem(last=False)
                
                self.cache[key] = value
    
    def get_all(self) -> Dict[int, int]:
        """Get snapshot of all key-value pairs without affecting LRU order."""
        with self.lock:
            return dict(self.cache)
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)