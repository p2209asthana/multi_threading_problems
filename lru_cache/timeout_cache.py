import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random

class TimeoutLRUCache:
    """
    LRU Cache with timeout-based locking to prevent deadlocks.
    """
    
    def __init__(self, capacity: int, timeout: float = 1.0):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = Lock()
        self.timeout = timeout
    
    def get(self, key: int) -> int:
        """Get value with timeout lock."""
        if not self.lock.acquire(timeout=self.timeout):
            raise TimeoutError("Failed to acquire lock within timeout")
        
        try:
            if key not in self.cache:
                return -1
            
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        finally:
            self.lock.release()
    
    def put(self, key: int, value: int) -> None:
        """Put value with timeout lock."""
        if not self.lock.acquire(timeout=self.timeout):
            raise TimeoutError("Failed to acquire lock within timeout")
        
        try:
            if key in self.cache:
                self.cache.pop(key)
                self.cache[key] = value
            else:
                if len(self.cache) >= self.capacity:
                    self.cache.popitem(last=False)
                self.cache[key] = value
        finally:
            self.lock.release()
    
    def get_all(self) -> Dict[int, int]:
        """Get all with timeout lock."""
        if not self.lock.acquire(timeout=self.timeout):
            raise TimeoutError("Failed to acquire lock within timeout")
        
        try:
            return dict(self.cache)
        finally:
            self.lock.release()
