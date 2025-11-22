import hashlib
from typing import Generator

class BloomFilter:
    """Space-efficient probabilistic data structure for duplicate detection"""
    
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        self.size = self._optimal_size(expected_items, false_positive_rate)
        self.hash_count = self._optimal_hash_count(expected_items, self.size)
        self.bit_array = bytearray((self.size + 7) // 8)
    
    def _optimal_size(self, n: int, p: float) -> int:
        """Calculate optimal bit array size"""
        import math
        return int(-(n * math.log(p)) / (math.log(2) ** 2))
    
    def _optimal_hash_count(self, n: int, m: int) -> int:
        """Calculate optimal number of hash functions"""
        import math
        return max(1, int((m / n) * math.log(2)))
    
    def _hashes(self, item: str) -> Generator[int, None, None]:
        """Generate multiple hash values for an item"""
        for i in range(self.hash_count):
            hash_obj = hashlib.md5(f"{item}{i}".encode())
            yield int(hash_obj.hexdigest(), 16) % self.size
    
    def add(self, item: str):
        """Add item to Bloom filter"""
        for hash_val in self._hashes(item):
            byte_index = hash_val // 8
            bit_index = hash_val % 8
            self.bit_array[byte_index] |= (1 << bit_index)
    
    def contains(self, item: str) -> bool:
        """Check if item might be in Bloom filter"""
        for hash_val in self._hashes(item):
            byte_index = hash_val // 8
            bit_index = hash_val % 8
            if not (self.bit_array[byte_index] & (1 << bit_index)):
                return False
        return True