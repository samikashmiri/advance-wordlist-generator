"""
Advanced tests for Wordlist Generator
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestAdvancedFeatures(unittest.TestCase):
    """Advanced feature tests"""
    
    def test_performance_optimization(self):
        """Test performance optimization features"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="advanced",
            first_name="performance",
            last_name="test"
        )
        
        # Test that performance stats are collected
        start_time = time.time()
        word_count = 0
        
        for word in generator.generate_with_callback():
            word_count += 1
            if word_count >= 100:  # Generate 100 words
                break
        
        elapsed = time.time() - start_time
        stats = generator.get_statistics()
        
        self.assertLess(elapsed, 10.0)  # Should complete quickly
        self.assertGreater(stats["words_per_second"], 0)
        self.assertGreater(stats["efficiency_score"], 0)
    
    def test_memory_management(self):
        """Test memory management features"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="advanced",
            first_name="memory",
            last_name="test"
        )
        
        # Generate words and check memory doesn't explode
        word_count = 0
        for word in generator.generate_with_callback():
            word_count += 1
            if word_count >= 500:  # Generate reasonable amount
                break
        
        stats = generator.get_statistics()
        self.assertLess(stats["peak_memory_mb"], 100.0)  # Should use reasonable memory
    
    def test_duplicate_prevention(self):
        """Test duplicate prevention mechanisms"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="advanced",
            first_name="duplicate",
            last_name="test"
        )
        
        # Collect all generated words
        generated_words = set()
        duplicate_count = 0
        
        def callback(word, count, duplicates):
            nonlocal duplicate_count
            duplicate_count = duplicates
            if word in generated_words:
                self.fail(f"Duplicate word generated: {word}")
            generated_words.add(word)
        
        # Generate words
        word_count = 0
        for word in generator.generate_with_callback(callback):
            word_count += 1
            if word_count >= 200:  # Generate 200 words
                break
        
        # Check that duplicates were prevented
        self.assertGreater(duplicate_count, 0)
        self.assertEqual(len(generated_words), word_count)  # All words should be unique

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_generation(self):
        """Test complete generation workflow"""
        from core.generator import create_generator
        from core.stream_writer import StreamingFileWriter
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            output_file = tmp_file.name
        
        try:
            # Generate wordlist
            generator = create_generator(
                mode="basic",
                first_name="integration",
                last_name="test",
                enable_leet=True,
                enable_capitals=True,
                append_numbers=True
            )
            
            # Write to file
            with StreamingFileWriter(output_file) as writer:
                word_count = 0
                for word in generator.generate_with_callback():
                    writer.add_word(word)
                    word_count += 1
                    if word_count >= 100:
                        break
            
            # Verify file content
            with open(output_file, 'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 100)
                
                # Check that various patterns are present
                content = ' '.join(lines)
                self.assertTrue(any(word in content for word in ['integration', 'test', 'INTEGRATION']))
                
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

if __name__ == '__main__':
    unittest.main()