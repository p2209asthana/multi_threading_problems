import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random


class ReadWriteLock:
    """Simple ReadWrite lock implementation."""
    
    def __init__(self):
        self._read_ready = Condition(RLock())
        self._readers = 0
    
    def acquire_read(self):
        """Acquire read lock."""
        with self._read_ready:
            self._readers += 1
    
    def release_read(self):
        """Release read lock."""
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notifyAll()
    
    def acquire_write(self):
        """Acquire write lock."""
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()
        # Note: Lock is held until release_write() - can't use 'with' here
    
    def release_write(self):
        """Release write lock."""
        self._read_ready.release()


class ReadWriteLRUCache:
    """
    LRU Cache optimized for read-heavy workloads using ReadWrite locks.
    Allows multiple concurrent readers but exclusive writers.
    """
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
        self.rw_lock = ReadWriteLock()
    
    def get(self, key: int) -> int:
        """Get value by key with read lock optimization."""
        # First try with read lock for quick lookup
        self.rw_lock.acquire_read()
        try:
            if key not in self.cache:
                return -1
            value = self.cache[key]
        finally:
            self.rw_lock.release_read()
        
        # Need write lock to update LRU order
        self.rw_lock.acquire_write()
        try:
            if key not in self.cache:  # Double-check
                return -1
            
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        finally:
            self.rw_lock.release_write()
    
    def put(self, key: int, value: int) -> None:
        """Put key-value pair with write lock."""
        self.rw_lock.acquire_write()
        try:
            if key in self.cache:
                self.cache.pop(key)
                self.cache[key] = value
            else:
                if len(self.cache) >= self.capacity:
                    self.cache.popitem(last=False)
                self.cache[key] = value
        finally:
            self.rw_lock.release_write()
    
    def get_all(self) -> Dict[int, int]:
        """Get snapshot with read lock."""
        self.rw_lock.acquire_read()
        try:
            return dict(self.cache)
        finally:
            self.rw_lock.release_read()