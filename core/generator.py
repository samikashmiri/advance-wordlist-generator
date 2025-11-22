import itertools
from typing import Set, Generator, List, Optional, Dict, Any
import time
import os
import sys

# Try to import psutil, but provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not installed. Performance monitoring will be limited.")
    print("💡 Install with: pip install psutil")

class PerformanceMonitor:
    """Monitor system performance during generation (with fallbacks)"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0  # Fallback value
            
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage"""
        if not PSUTIL_AVAILABLE:
            return 0.0  # Fallback value
            
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    @staticmethod
    def should_continue(max_memory_mb: int = 500) -> bool:
        """Check if we should continue based on system resources"""
        if not PSUTIL_AVAILABLE:
            return True  # Always continue if psutil not available
            
        return PerformanceMonitor.get_memory_usage() < max_memory_mb
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information (with fallbacks)"""
        if not PSUTIL_AVAILABLE:
            return {
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "available_memory_gb": 0,
                "system_load": [0, 0, 0],
                "psutil_available": False
            }
            
        try:
            return {
                "memory_usage_mb": PerformanceMonitor.get_memory_usage(),
                "cpu_usage_percent": PerformanceMonitor.get_cpu_usage(),
                "available_memory_gb": psutil.virtual_memory().available / (1024**3),
                "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "psutil_available": True
            }
        except:
            return {
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "available_memory_gb": 0,
                "system_load": [0, 0, 0],
                "psutil_available": False
            }

class BaseWordlistGenerator:
    """Base class with common functionality and performance tracking"""
    
    def __init__(self, first_name: str, last_name: str, middle_name: Optional[str] = None,
                 max_length: int = 15, min_length: int = 3, enable_leet: bool = True,
                 enable_capitals: bool = True, append_numbers: bool = True,
                 prepend_numbers: bool = True, special_chars: bool = True):
        
        self.first_name = first_name.strip().lower()
        self.last_name = last_name.strip().lower()
        self.middle_name = middle_name.strip().lower() if middle_name else None
        
        self.max_length = max_length
        self.min_length = min_length
        self.enable_leet = enable_leet
        self.enable_capitals = enable_capitals
        self.append_numbers = append_numbers
        self.prepend_numbers = prepend_numbers
        self.special_chars = special_chars
        
        # Performance and statistics tracking
        self.generated_count = 0
        self.duplicate_count = 0
        self.start_time = None
        self.performance_stats = {
            "peak_memory_mb": 0,
            "average_cpu_percent": 0,
            "total_processing_time": 0,
            "words_per_second": 0,
            "variations_processed": 0,
            "psutil_available": PSUTIL_AVAILABLE
        }
        
        # Initialize base words
        self.base_words = self._generate_smart_name_combinations()
    
    def _generate_smart_name_combinations(self) -> Set[str]:
        """Generate smart name combinations without explosion"""
        combinations = set()
        
        # Core individual names
        names = []
        if self.first_name:
            names.append(self.first_name)
        if self.last_name:
            names.append(self.last_name)
        if self.middle_name:
            names.append(self.middle_name)
        
        # Add individual names with basic variations
        for name in names:
            combinations.add(name)
            combinations.add(name.upper())
            combinations.add(name.capitalize())
        
        # Essential combinations (limit to avoid explosion)
        if self.first_name and self.last_name:
            # Main combinations
            main_combos = [
                self.first_name + self.last_name,
                self.last_name + self.first_name,
                self.first_name + '_' + self.last_name,
                self.first_name + '.' + self.last_name,
                self.first_name + '-' + self.last_name,
                self.first_name[0] + self.last_name,
                self.first_name + self.last_name[0],
                self.first_name[0] + self.last_name[0],
                self.first_name + '123',
                self.last_name + '123',
                'admin' + self.last_name,
                self.first_name + 'admin'
            ]
            combinations.update(main_combos)
        
        # Middle name combinations (limited)
        if self.middle_name:
            limited_middle_combos = [
                self.first_name + self.middle_name[0] + self.last_name,
                self.first_name[0] + self.middle_name[0] + self.last_name[0],
                self.middle_name + self.last_name,
                self.first_name + self.middle_name
            ]
            combinations.update(limited_middle_combos)
        
        # Filter by length and return
        return {word for word in combinations if self.min_length <= len(word) <= self.max_length}
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        current_memory = PerformanceMonitor.get_memory_usage()
        current_cpu = PerformanceMonitor.get_cpu_usage()
        
        # Update peak memory (only if psutil is available)
        if PSUTIL_AVAILABLE:
            self.performance_stats["peak_memory_mb"] = max(
                self.performance_stats["peak_memory_mb"], 
                current_memory
            )
            
            # Update average CPU (simple moving average)
            cpu_samples = self.performance_stats.get("_cpu_samples", [])
            cpu_samples.append(current_cpu)
            if len(cpu_samples) > 10:  # Keep last 10 samples
                cpu_samples.pop(0)
            self.performance_stats["_cpu_samples"] = cpu_samples
            self.performance_stats["average_cpu_percent"] = sum(cpu_samples) / len(cpu_samples)
        
        # Update processing time (always available)
        if self.start_time:
            self.performance_stats["total_processing_time"] = time.time() - self.start_time
            self.performance_stats["words_per_second"] = (
                self.generated_count / self.performance_stats["total_processing_time"] 
                if self.performance_stats["total_processing_time"] > 0 else 0
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive generation statistics"""
        base_stats = {
            "base_combinations": len(self.base_words),
            "total_generated": self.generated_count,
            "duplicates_prevented": self.duplicate_count,
            "generation_time": self.performance_stats["total_processing_time"],
            "words_per_second": self.performance_stats["words_per_second"],
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "max_length": self.max_length,
            "min_length": self.min_length,
            "performance_monitoring": PSUTIL_AVAILABLE
        }
        
        # Add performance stats if available
        if PSUTIL_AVAILABLE:
            base_stats.update({
                "peak_memory_mb": round(self.performance_stats["peak_memory_mb"], 2),
                "average_cpu_percent": round(self.performance_stats["average_cpu_percent"], 1),
                "efficiency_score": self._calculate_efficiency_score()
            })
        else:
            base_stats.update({
                "peak_memory_mb": "N/A (install psutil)",
                "average_cpu_percent": "N/A (install psutil)", 
                "efficiency_score": "N/A (install psutil)"
            })
        
        return base_stats
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate an efficiency score based on performance metrics"""
        if not PSUTIL_AVAILABLE or self.performance_stats["total_processing_time"] == 0:
            return 0.0
        
        # Factors: words per second (higher better), memory usage (lower better)
        wps_score = min(self.performance_stats["words_per_second"] / 1000, 1.0)  # Normalize
        memory_score = max(0, 1 - (self.performance_stats["peak_memory_mb"] / 500))  # Lower memory better
        
        efficiency = (wps_score * 0.6 + memory_score * 0.4) * 100
        return round(efficiency, 1)
    
    def _should_continue_generation(self) -> bool:
        """Check if generation should continue based on system resources"""
        if not PSUTIL_AVAILABLE:
            return True  # Always continue if psutil not available
            
        if not PerformanceMonitor.should_continue():
            return False
        
        # Additional safety checks
        if self.performance_stats["peak_memory_mb"] > 450:  # Getting close to limit
            return False
            
        return True
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get insights and recommendations based on performance"""
        insights = {
            "status": "optimal",
            "recommendations": [],
            "bottlenecks": [],
            "psutil_available": PSUTIL_AVAILABLE
        }
        
        if not PSUTIL_AVAILABLE:
            insights["recommendations"].append("Install psutil for detailed performance monitoring")
            return insights
        
        # Memory analysis
        if self.performance_stats["peak_memory_mb"] > 300:
            insights["status"] = "high_memory"
            insights["recommendations"].append("Consider using Basic mode for lower memory usage")
            insights["bottlenecks"].append("Memory usage is high")
        
        # Speed analysis
        if self.performance_stats["words_per_second"] < 100:
            insights["status"] = "slow_generation"
            insights["recommendations"].append("Try disabling some pattern options to improve speed")
            insights["bottlenecks"].append("Generation speed is below optimal")
        
        # CPU analysis
        if self.performance_stats["average_cpu_percent"] > 80:
            insights["status"] = "high_cpu"
            insights["recommendations"].append("System is under heavy load, consider closing other applications")
            insights["bottlenecks"].append("CPU usage is high")
        
        return insights

class BasicWordlistGenerator(BaseWordlistGenerator):
    """Efficient Basic Mode - Fast and memory friendly"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from .patterns import BasicPatternGenerator
        self.pattern_generator = BasicPatternGenerator()
    
    def generate_with_callback(self, callback=None) -> Generator[str, None, None]:
        """Generate words efficiently with performance tracking"""
        self.start_time = time.time()
        self.generated_count = 0
        self.duplicate_count = 0
        seen_words = set()
        
        # Performance monitoring setup
        last_performance_update = time.time()
        
        for word in self.base_words:
            # Check system resources periodically
            if time.time() - last_performance_update > 0.5:  # Update every 0.5 seconds
                self._update_performance_stats()
                last_performance_update = time.time()
                
                if not self._should_continue_generation():
                    if callback:
                        callback("[SYSTEM] Generation stopped due to high memory usage", 
                               self.generated_count, self.duplicate_count)
                    break
            
            # Generate variations in a controlled way
            for variant in self._generate_efficient_variations(word):
                if not self._should_continue_generation():
                    break
                    
                if (variant not in seen_words and 
                    self.min_length <= len(variant) <= self.max_length):
                    
                    seen_words.add(variant)
                    self.generated_count += 1
                    self.performance_stats["variations_processed"] += 1
                    
                    if callback:
                        callback(variant, self.generated_count, self.duplicate_count)
                    yield variant
                else:
                    self.duplicate_count += 1
        
        # Final performance update
        self._update_performance_stats()
    
    def _generate_efficient_variations(self, word: str) -> Generator[str, None, None]:
        """Generate variations without combinatorial explosion"""
        # Original word
        yield word
        
        # Capitalization
        if self.enable_capitals:
            yield word.upper()
            yield word.capitalize()
            if len(word) > 3:
                yield word[0].upper() + word[1:].lower()
        
        # Leet speak (limited)
        if self.enable_leet:
            yield from self.pattern_generator.smart_leet_transform(word)
        
        # Numbers (limited combinations)
        if self.append_numbers:
            yield from self.pattern_generator.smart_number_append(word)
        
        if self.prepend_numbers:
            yield from self.pattern_generator.smart_number_prepend(word)
        
        # Special chars
        if self.special_chars:
            yield from self.pattern_generator.smart_special_chars(word)
        
        # Limited combined patterns (leet + numbers)
        if self.enable_leet and self.append_numbers:
            leet_variants = list(self.pattern_generator.smart_leet_transform(word))
            for leet_word in leet_variants[:3]:  # Limit to first 3 leet variants
                for num_word in self.pattern_generator.smart_number_append(leet_word):
                    yield num_word

class AdvancedWordlistGenerator(BaseWordlistGenerator):
    """Optimized Advanced Mode - Comprehensive but with safeguards"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from .patterns import AdvancedPatternGenerator
        from .optimizations import BloomFilter
        
        self.pattern_generator = AdvancedPatternGenerator()
        # Smaller bloom filter for performance
        self.bloom_filter = BloomFilter(expected_items=1000000, false_positive_rate=0.01)
        self.max_variations_per_word = 500  # Safety limit per base word
        self._current_word_variations = 0
    
    def generate_with_callback(self, callback=None) -> Generator[str, None, None]:
        """Generate comprehensive variations with performance safeguards"""
        self.start_time = time.time()
        self.generated_count = 0
        self.duplicate_count = 0
        
        # Performance monitoring setup
        last_performance_update = time.time()
        system_info_updates = 0
        
        for word in self.base_words:
            if not self._should_continue_generation():
                if callback:
                    callback("[SYSTEM] Generation stopped due to resource limits", 
                           self.generated_count, self.duplicate_count)
                break
            
            self._current_word_variations = 0
            variation_count = 0
            
            for variant in self._generate_optimized_variations(word):
                if not self._should_continue_generation():
                    break
                    
                # Update performance stats periodically
                if time.time() - last_performance_update > 0.3:  # Update every 0.3 seconds
                    self._update_performance_stats()
                    last_performance_update = time.time()
                    system_info_updates += 1
                    
                    # Send system info update occasionally
                    if system_info_updates % 5 == 0 and callback and PSUTIL_AVAILABLE:
                        system_info = PerformanceMonitor.get_system_info()
                        callback(f"[SYSTEM] Memory: {system_info['memory_usage_mb']:.1f}MB, CPU: {system_info['cpu_usage_percent']:.1f}%", 
                               self.generated_count, self.duplicate_count)
                    elif system_info_updates % 10 == 0 and callback:
                        # Basic progress update without system info
                        callback(f"[SYSTEM] Progress: {self.generated_count} words generated", 
                               self.generated_count, self.duplicate_count)
                
                if variation_count >= self.max_variations_per_word:
                    if callback:
                        callback(f"[SYSTEM] Limited variations for: {word}", 
                               self.generated_count, self.duplicate_count)
                    break
                    
                if (self.min_length <= len(variant) <= self.max_length and 
                    not self.bloom_filter.contains(variant)):
                    
                    self.bloom_filter.add(variant)
                    self.generated_count += 1
                    variation_count += 1
                    self.performance_stats["variations_processed"] += 1
                    
                    if callback:
                        callback(variant, self.generated_count, self.duplicate_count)
                    yield variant
                else:
                    self.duplicate_count += 1
        
        # Final performance update
        self._update_performance_stats()
        
        # Send completion message
        if callback:
            insights = self.get_performance_insights()
            if PSUTIL_AVAILABLE:
                callback(f"[SYSTEM] Generation complete. Efficiency: {self._calculate_efficiency_score()}%", 
                       self.generated_count, self.duplicate_count)
            else:
                callback(f"[SYSTEM] Generation complete. {self.generated_count} words generated", 
                       self.generated_count, self.duplicate_count)
    
    def _generate_optimized_variations(self, word: str) -> Generator[str, None, None]:
        """Generate optimized variations without memory explosion"""
        variations = set()
        
        # Phase 1: Core variations
        variations.add(word)
        
        # Capitalization
        if self.enable_capitals:
            variations.update(self.pattern_generator.optimized_capitalization(word))
        
        # Leet speak with limits
        if self.enable_leet:
            leet_variants = self.pattern_generator.optimized_leet_transform(word)
            # Take only first 30 leet variants to avoid explosion
            variations.update(list(leet_variants)[:30])
        
        # Phase 2: Apply numbers to core variations (limited)
        number_variations = set()
        if self.append_numbers or self.prepend_numbers:
            core_variants = list(variations)[:50]  # Limit to first 50 variants
            for variant in core_variants:
                if self.append_numbers:
                    number_variations.update(self.pattern_generator.optimized_number_append(variant))
                if self.prepend_numbers:
                    number_variations.update(self.pattern_generator.optimized_number_prepend(variant))
        
        variations.update(number_variations)
        
        # Phase 3: Apply special chars to core variations (limited)
        special_variations = set()
        if self.special_chars:
            core_variants = list(variations)[:50]  # Limit to first 50 variants
            for variant in core_variants:
                special_variations.update(self.pattern_generator.optimized_special_chars(variant))
        
        variations.update(special_variations)
        
        # Yield all collected variations
        for variant in variations:
            if self._current_word_variations >= self.max_variations_per_word:
                break
            self._current_word_variations += 1
            yield variant

class ProgressNotifier:
    """Advanced progress notification system for real-time updates"""
    
    def __init__(self, total_estimated_words: int = 1000):
        self.total_estimated = total_estimated_words
        self.start_time = time.time()
        self.phase = "initializing"
        self.last_progress_report = 0
        self.milestones = {
            100: "First 100 words generated",
            1000: "First 1,000 words reached", 
            5000: "5,000 words milestone",
            10000: "10,000 words milestone",
            50000: "50,000 words milestone"
        }
    
    def get_progress_update(self, current_count: int, duplicates: int, current_word: str = "") -> Dict[str, Any]:
        """Get comprehensive progress update"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calculate progress percentage (estimated)
        progress = min(current_count / self.total_estimated, 1.0) if self.total_estimated > 0 else 0
        
        # Calculate metrics
        words_per_second = current_count / elapsed if elapsed > 0 else 0
        
        # Calculate ETA
        if words_per_second > 0:
            remaining = self.total_estimated - current_count
            eta_seconds = remaining / words_per_second
            eta_formatted = self._format_time(eta_seconds)
        else:
            eta_formatted = "Calculating..."
        
        # Check for milestones
        milestone_message = ""
        for milestone, message in self.milestones.items():
            if current_count >= milestone and current_count - 100 < milestone:
                milestone_message = f"🎯 {message}"
                break
        
        return {
            "progress": progress,
            "current_count": current_count,
            "duplicates_prevented": duplicates,
            "words_per_second": words_per_second,
            "elapsed_time": self._format_time(elapsed),
            "eta": eta_formatted,
            "efficiency": f"{words_per_second:.1f} words/sec",
            "milestone": milestone_message,
            "current_phase": self.phase,
            "sample_word": current_word[-20:] if current_word else ""  # Last 20 chars
        }
    
    def set_phase(self, phase: str):
        """Update the current phase"""
        self.phase = phase
    
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.0f}m {seconds % 60:.0f}s"
        else:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            return f"{hours:.0f}h {minutes:.0f}m"

# Factory function
def create_generator(mode: str, **kwargs) -> BaseWordlistGenerator:
    """
    Create a wordlist generator based on the specified mode.
    
    Args:
        mode: "basic" for memory-efficient generation, "advanced" for comprehensive patterns
        **kwargs: Generator configuration parameters
    
    Returns:
        BaseWordlistGenerator instance
    """
    if mode == "advanced":
        return AdvancedWordlistGenerator(**kwargs)
    else:  # basic
        return BasicWordlistGenerator(**kwargs)

def get_generator_capabilities() -> Dict[str, Any]:
    """Get information about generator capabilities and limitations"""
    return {
        "basic_mode": {
            "estimated_words": "5,000 - 20,000",
            "memory_usage": "10-50 MB",
            "speed": "Fast",
            "best_for": "Quick tests, limited resources",
            "limitations": "Limited pattern combinations"
        },
        "advanced_mode": {
            "estimated_words": "20,000 - 100,000", 
            "memory_usage": "50-200 MB",
            "speed": "Moderate to Slow",
            "best_for": "Comprehensive testing",
            "limitations": "Higher resource usage"
        },
        "performance_notes": [
            "Memory usage depends on name length and pattern options",
            "Disabling patterns improves speed and reduces memory",
            "Basic mode is recommended for most use cases",
            "Advanced mode uses Bloom filter for duplicate detection",
            f"Performance monitoring: {'Enabled' if PSUTIL_AVAILABLE else 'Disabled (install psutil)'}"
        ]
    }

# Performance testing utility (works without psutil)
def benchmark_generator(generator: BaseWordlistGenerator, sample_size: int = 1000) -> Dict[str, Any]:
    """Benchmark generator performance with a sample"""
    start_time = time.time()
    
    words_generated = 0
    for word in generator.generate_with_callback():
        words_generated += 1
        if words_generated >= sample_size:
            break
    
    end_time = time.time()
    
    results = {
        "sample_size": sample_size,
        "total_time": end_time - start_time,
        "words_per_second": sample_size / (end_time - start_time) if (end_time - start_time) > 0 else 0,
        "performance_monitoring": PSUTIL_AVAILABLE
    }
    
    # Add memory info if psutil is available
    if PSUTIL_AVAILABLE:
        try:
            start_memory = PerformanceMonitor.get_memory_usage()
            # Re-run to measure memory (simplified approach)
            temp_generator = create_generator(
                mode=generator.__class__.__name__.lower().replace('wordlistgenerator', ''),
                first_name="benchmark",
                last_name="test"
            )
            
            for word in temp_generator.generate_with_callback():
                if temp_generator.generated_count >= 100:
                    break
                    
            end_memory = PerformanceMonitor.get_memory_usage()
            results["memory_increase_mb"] = end_memory - start_memory
            results["efficiency_rating"] = "Excellent" if (end_memory - start_memory) < 10 else "Good"
        except:
            results["memory_increase_mb"] = "Measurement failed"
            results["efficiency_rating"] = "Unknown"
    else:
        results["memory_increase_mb"] = "Install psutil for memory metrics"
        results["efficiency_rating"] = "Unknown"
    
    return results

if __name__ == "__main__":
    # Test the generator
    print("🧪 Testing Wordlist Generator...")
    
    # Test basic generator
    basic_gen = create_generator(
        mode="basic",
        first_name="john",
        last_name="doe",
        max_length=12,
        min_length=3
    )
    
    print(f"✅ Basic Generator Created - {len(basic_gen.base_words)} base combinations")
    
    # Test advanced generator  
    advanced_gen = create_generator(
        mode="advanced", 
        first_name="john",
        last_name="doe",
        max_length=12,
        min_length=3
    )
    
    print(f"✅ Advanced Generator Created - {len(advanced_gen.base_words)} base combinations")
    print(f"📊 Performance Monitoring: {'Enabled' if PSUTIL_AVAILABLE else 'Disabled'}")
    if not PSUTIL_AVAILABLE:
        print("💡 Install psutil for detailed performance metrics: pip install psutil")
    print("🎯 Generator is ready for use!")