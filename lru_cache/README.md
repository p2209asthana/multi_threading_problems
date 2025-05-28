# LeetCode-Style Problem: Thread-Safe LRU Cache

## Problem Statement

Design a **thread-safe** data structure that follows the constraints of a **Least Recently Used (LRU) cache**.

Implement the `ThreadSafeLRUCache` class:

* `ThreadSafeLRUCache(int capacity)` Initialize the LRU cache with **positive** size `capacity`.
* `int get(int key)` Return the value of the `key` if the key exists, otherwise return `-1`. This operation counts as a "use" of the key.
* `void put(int key, int value)` Update the value of the `key` if the `key` exists. Otherwise, add the `key-value` pair to the cache. If the number of keys exceeds the `capacity` from this operation, **evict** the least recently used key.

**The `get` and `put` operations must be thread-safe and support concurrent access from multiple threads.**

## Constraints

* `1 <= capacity <= 3000`
* `0 <= key <= 10^4`
* `0 <= value <= 10^5`
* At most `2 * 10^5` calls will be made to `get` and `put`.
* **Multiple threads may call `get` and `put` concurrently.**

## Example

```python
# Example 1:
cache = ThreadSafeLRUCache(2)

# Thread 1:
cache.put(1, 1)
cache.put(2, 2)
cache.get(1)    # returns 1

# Thread 2 (concurrent):
cache.put(3, 3) # evicts key 2
cache.get(2)    # returns -1 (not found)

# Thread 1 (concurrent):
cache.get(3)    # returns 3
cache.get(1)    # returns 1

# Thread 2 (concurrent):
cache.put(4, 4) # evicts key 3
cache.get(1)    # returns 1
cache.get(3)    # returns -1 (not found)
cache.get(4)    # returns 4