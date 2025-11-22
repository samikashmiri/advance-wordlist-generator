"""
Basic functionality tests for Wordlist Generator
Windows-compatible version
"""

import unittest
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_first_name = "john"
        self.test_last_name = "doe"
        self.test_middle_name = "test"
    
    def test_generator_creation(self):
        """Test that generators can be created"""
        from core.generator import create_generator
        
        # Test basic generator
        basic_gen = create_generator(
            mode="basic",
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        self.assertIsNotNone(basic_gen)
        self.assertGreater(len(basic_gen.base_words), 0)
        
        # Test advanced generator
        advanced_gen = create_generator(
            mode="advanced", 
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        self.assertIsNotNone(advanced_gen)
        self.assertGreater(len(advanced_gen.base_words), 0)
    
    def test_name_combinations(self):
        """Test name combination generation"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="basic",
            first_name="alice",
            last_name="smith"
        )
        
        # Check that basic combinations are generated
        combinations = generator.base_words
        self.assertIn("alice", combinations)
        self.assertIn("smith", combinations)
        self.assertIn("alicesmith", combinations)
    
    def test_statistics(self):
        """Test statistics generation"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="basic",
            first_name="test",
            last_name="user"
        )
        
        stats = generator.get_statistics()
        self.assertIn("base_combinations", stats)
        self.assertIn("total_generated", stats)
        self.assertIn("generation_time", stats)
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="basic",
            first_name="test",
            last_name="user"
        )
        
        # Generate a few words to trigger performance monitoring
        word_count = 0
        for word in generator.generate_with_callback():
            word_count += 1
            if word_count >= 10:  # Just test a few words
                break
        
        stats = generator.get_statistics()
        self.assertIn("peak_memory_mb", stats)
        self.assertIn("efficiency_score", stats)
    
    def test_file_creation(self):
        """Test that files are created properly"""
        from core.generator import create_generator
        from core.stream_writer import StreamingFileWriter
        
        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            output_file = tmp_file.name
        
        try:
            generator = create_generator(
                mode="basic",
                first_name=self.test_first_name,
                last_name=self.test_last_name
            )
            
            # Generate and write words
            with StreamingFileWriter(output_file) as writer:
                word_count = 0
                for word in generator.generate_with_callback():
                    writer.add_word(word)
                    word_count += 1
                    if word_count >= 50:  # Limit for testing
                        break
            
            # Check file was created and has content
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertGreater(len(content), 0)
                self.assertGreaterEqual(content.count('\n'), 10)  # At least 10 lines
                
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_empty_names(self):
        """Test handling of empty names"""
        from core.generator import create_generator
        
        # Should handle empty first name gracefully
        with self.assertRaises(Exception):
            create_generator(mode="basic", first_name="", last_name="doe")
        
        # Should handle empty last name gracefully  
        with self.assertRaises(Exception):
            create_generator(mode="basic", first_name="john", last_name="")
    
    def test_special_characters_in_names(self):
        """Test names with special characters"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="basic",
            first_name="john-doe",
            last_name="smith_jr"
        )
        
        self.assertIsNotNone(generator)
        self.assertGreater(len(generator.base_words), 0)

class TestPatterns(unittest.TestCase):
    """Test pattern generation"""
    
    def test_leet_patterns(self):
        """Test leet speak patterns"""
        from core.generator import create_generator
        
        generator = create_generator(
            mode="basic",
            first_name="test",
            last_name="user",
            enable_leet=True,
            enable_capitals=False,
            append_numbers=False,
            prepend_numbers=False,
            special_chars=False
        )
        
        # Generate words and check for leet patterns
        found_leet = False
        word_count = 0
        for word in generator.generate_with_callback():
            if any(char in word for char in ['4', '3', '1', '0', '5', '7']):
                found_leet = True
            word_count += 1
            if word_count >= 20:  # Check first 20 words
                break
        
        self.assertTrue(found_leet, "Should generate leet speak variations")

if __name__ == '__main__':
    unittest.main()