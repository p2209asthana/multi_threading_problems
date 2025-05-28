import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random

class SegmentedLRUCache:
    """
    Segmented LRU Cache that divides keys across multiple cache segments
    to reduce lock contention under high concurrency.
    """
    
    def __init__(self, capacity: int, num_segments: int = 16):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.num_segments = num_segments
        segment_capacity = max(1, capacity // num_segments)
        
        self.segments = [
            ThreadSafeLRUCache(segment_capacity) 
            for _ in range(num_segments)
        ]
    
    def _get_segment(self, key: int) -> ThreadSafeLRUCache:
        """Get segment for given key using hash."""
        return self.segments[hash(key) % self.num_segments]
    
    def get(self, key: int) -> int:
        """Get value from appropriate segment."""
        return self._get_segment(key).get(key)
    
    def put(self, key: int, value: int) -> None:
        """Put value in appropriate segment."""
        self._get_segment(key).put(key, value)
    
    def get_all(self) -> Dict[int, int]:
        """Get all key-value pairs from all segments."""
        result = {}
        for segment in self.segments:
            result.update(segment.get_all())
        return result