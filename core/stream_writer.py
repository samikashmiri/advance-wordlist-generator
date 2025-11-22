import os
import time
import sys

# Try to import psutil, but provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available in stream_writer. Memory monitoring will be limited.")

class PerformanceMonitor:
    """Performance monitoring with fallbacks for stream writer"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0
            
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    @staticmethod
    def should_continue(max_memory_mb: int = 500) -> bool:
        """Check if we should continue based on system resources"""
        if not PSUTIL_AVAILABLE:
            return True  # Always continue if psutil not available
            
        return PerformanceMonitor.get_memory_usage() < max_memory_mb

class StreamingFileWriter:
    """Write words directly to file without storing in memory"""
    
    def __init__(self, output_file: str, buffer_size: int = 1000):
        self.output_file = output_file
        self.buffer_size = buffer_size
        self.buffer = []
        self.word_count = 0
        self.file_obj = None
        self.start_time = time.time()
        
        # Performance tracking (with fallbacks)
        self.peak_memory = 0
        self.total_words_processed = 0
        self.psutil_available = PSUTIL_AVAILABLE
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    def __enter__(self):
        self.file_obj = open(self.output_file, 'w', encoding='utf-8', buffering=8192)
        return self
    
    def add_word(self, word: str):
        """Add word to buffer, flush when full"""
        self.buffer.append(word + '\n')
        self.word_count += 1
        self.total_words_processed += 1
        
        # Update peak memory usage (only if psutil available)
        if PSUTIL_AVAILABLE:
            current_memory = PerformanceMonitor.get_memory_usage()
            self.peak_memory = max(self.peak_memory, current_memory)
        
        # Flush buffer when full or memory getting high (if we can monitor it)
        if (len(self.buffer) >= self.buffer_size or 
            (PSUTIL_AVAILABLE and PerformanceMonitor.get_memory_usage() > 400)):
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Write buffer to file and clear"""
        if self.buffer:
            self.file_obj.writelines(self.buffer)
            self.buffer.clear()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush_buffer()
        if self.file_obj:
            self.file_obj.close()
    
    def get_stats(self):
        """Get writing statistics"""
        elapsed = time.time() - self.start_time
        stats = {
            "word_count": self.word_count,
            "total_processing_time": elapsed,
            "words_per_second": self.word_count / elapsed if elapsed > 0 else 0,
            "performance_monitoring": PSUTIL_AVAILABLE
        }
        
        # Add memory stats if available
        if PSUTIL_AVAILABLE:
            stats["peak_memory_mb"] = round(self.peak_memory, 2)
        else:
            stats["peak_memory_mb"] = "N/A (install psutil)"
            
        return stats

class OptimizedStreamingFileWriter:
    """Enhanced version with better performance monitoring"""
    
    def __init__(self, output_file: str, buffer_size: int = 5000):
        self.output_file = output_file
        self.buffer_size = buffer_size
        self.buffer = []
        self.word_count = 0
        self.file_obj = None
        self.start_time = time.time()
        
        # Performance tracking
        self.peak_memory = 0
        self.total_words_processed = 0
        self.flush_count = 0
        self.psutil_available = PSUTIL_AVAILABLE
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    def __enter__(self):
        self.file_obj = open(self.output_file, 'w', encoding='utf-8', buffering=8192)
        return self
    
    def add_word(self, word: str):
        """Add word to buffer with performance checks"""
        self.buffer.append(word + '\n')
        self.word_count += 1
        self.total_words_processed += 1
        
        # Update peak memory usage if psutil available
        if PSUTIL_AVAILABLE:
            current_memory = PerformanceMonitor.get_memory_usage()
            self.peak_memory = max(self.peak_memory, current_memory)
        
        # Flush buffer when full
        if len(self.buffer) >= self.buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Write buffer to file and clear"""
        if self.buffer:
            self.file_obj.writelines(self.buffer)
            self.buffer.clear()
            self.flush_count += 1
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._flush_buffer()
        if self.file_obj:
            self.file_obj.close()
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        elapsed = time.time() - self.start_time
        stats = {
            "word_count": self.word_count,
            "peak_memory_mb": self.peak_memory if PSUTIL_AVAILABLE else "N/A",
            "total_processing_time": elapsed,
            "words_per_second": self.word_count / elapsed if elapsed > 0 else 0,
            "flush_count": self.flush_count,
            "average_buffer_usage": self.word_count / self.flush_count if self.flush_count > 0 else 0,
            "performance_monitoring": PSUTIL_AVAILABLE
        }
        
        return stats
    
    def get_efficiency_score(self) -> float:
        """Calculate an efficiency score for the writing process"""
        stats = self.get_performance_stats()
        
        if not isinstance(stats["words_per_second"], (int, float)) or stats["words_per_second"] == 0:
            return 0.0
        
        # Score based on words per second (higher is better)
        wps_score = min(stats["words_per_second"] / 1000, 1.0)
        
        # If we have memory info, include it in the score
        if PSUTIL_AVAILABLE and isinstance(stats["peak_memory_mb"], (int, float)):
            memory_score = max(0, 1 - (stats["peak_memory_mb"] / 500))
            efficiency = (wps_score * 0.7 + memory_score * 0.3) * 100
        else:
            efficiency = wps_score * 100
            
        return round(efficiency, 1)

# Backward compatibility - use StreamingFileWriter as the main class
# OptimizedStreamingFileWriter can be used for more advanced scenarios