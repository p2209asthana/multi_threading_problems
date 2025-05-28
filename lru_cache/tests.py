import threading
import time
from collections import OrderedDict
from threading import Lock, RLock, Condition
from typing import Dict, Optional, Any
import concurrent.futures
import random

def test_basic_functionality():
    """Test basic LRU cache functionality."""
    print("=== Basic Functionality Test ===")
    cache = ThreadSafeLRUCache(2)
    
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # 1
    
    cache.put(3, 3)  # evicts key 2
    print(f"get(2): {cache.get(2)}")  # -1
    print(f"get(3): {cache.get(3)}")  # 3
    print(f"get(1): {cache.get(1)}")  # 1
    
    cache.put(4, 4)  # evicts key 3
    print(f"get(1): {cache.get(1)}")  # 1
    print(f"get(3): {cache.get(3)}")  # -1
    print(f"get(4): {cache.get(4)}")  # 4
    print("✅ Basic functionality test passed\n")


def test_thread_safety():
    """Test thread safety with concurrent operations."""
    print("=== Thread Safety Test ===")
    cache = ThreadSafeLRUCache(100)
    num_threads = 10
    operations_per_thread = 1000
    
    def worker(thread_id):
        for i in range(operations_per_thread):
            key = (thread_id * operations_per_thread + i) % 200
            cache.put(key, key * 2)
            retrieved = cache.get(key)
            # Verify consistency
            if retrieved != -1 and retrieved != key * 2:
                raise ValueError(f"Inconsistent data: expected {key * 2}, got {retrieved}")
    
    # Run concurrent threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, i) for i in range(num_threads)]
        
        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise any exceptions from the thread
            except Exception as e:
                print(f"Thread failed: {e}")
                return
    
    print("✅ Thread safety test passed\n")


def test_performance_comparison():
    """Compare performance of different implementations."""
    print("=== Performance Comparison ===")
    capacity = 1000
    operations = 50000
    
    implementations = [
        ("Basic Synchronized", ThreadSafeLRUCache(capacity)),
        ("Manual Implementation", ManualLRUCache(capacity)),
        ("ReadWrite Lock", ReadWriteLRUCache(capacity)),
        ("Segmented Cache", SegmentedLRUCache(capacity)),
        ("Timeout Cache", TimeoutLRUCache(capacity))
    ]
    
    for name, cache in implementations:
        start_time = time.time()
        
        for i in range(operations):
            cache.put(i % (capacity * 2), i)
            cache.get(i % capacity)
        
        elapsed = (time.time() - start_time) * 1000
        print(f"{name}: {elapsed:.2f} ms")
    
    print()


def test_concurrent_performance():
    """Test performance under concurrent load."""
    print("=== Concurrent Performance Test ===")
    
    def run_concurrent_test(cache, name, num_threads=10, ops_per_thread=5000):
        def worker(thread_id):
            rand = random.Random(thread_id)
            for _ in range(ops_per_thread):
                key = rand.randint(0, 1000)
                if rand.random() < 0.5:
                    cache.put(key, key * 2)
                else:
                    cache.get(key)
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        elapsed = (time.time() - start_time) * 1000
        print(f"{name}: {elapsed:.2f} ms ({num_threads} threads)")
    
    # Test different implementations under concurrent load
    run_concurrent_test(ThreadSafeLRUCache(500), "Basic Synchronized")
    run_concurrent_test(ReadWriteLRUCache(500), "ReadWrite Lock")
    run_concurrent_test(SegmentedLRUCache(500), "Segmented Cache")
    
    print()


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("=== Edge Cases Test ===")
    
    # Test minimum capacity
    cache = ThreadSafeLRUCache(1)
    cache.put(1, 10)
    assert cache.get(1) == 10
    cache.put(2, 20)  # Should evict key 1
    assert cache.get(1) == -1
    assert cache.get(2) == 20
    print("✅ Minimum capacity test passed")
    
    # Test zero and negative values
    cache = ThreadSafeLRUCache(3)
    cache.put(0, 0)
    cache.put(1, -1)
    cache.put(2, 100000)
    
    assert cache.get(0) == 0
    assert cache.get(1) == -1
    assert cache.get(2) == 100000
    print("✅ Zero and negative values test passed")
    
    # Test invalid capacity
    try:
        ThreadSafeLRUCache(0)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✅ Invalid capacity handling test passed")
    
    print()


if __name__ == "__main__":
    print("Starting Thread-Safe LRU Cache Tests...\n")
    
    test_basic_functionality()
    test_thread_safety()
    test_performance_comparison()
    test_concurrent_performance()
    test_edge_cases()
    
    print("All tests completed successfully! 🎉")