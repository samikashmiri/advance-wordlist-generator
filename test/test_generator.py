import unittest
import tempfile
import os
from core.generator import create_generator
from core.stream_writer import StreamingFileWriter

class TestWordlistGenerator(unittest.TestCase):
    """Comprehensive tests for wordlist generator"""
    
    def setUp(self):
        self.test_first_name = "john"
        self.test_last_name = "doe"
        self.test_middle_name = "test"
    
    def test_basic_generator_creation(self):
        """Test basic generator creation"""
        generator = create_generator(
            mode="basic",
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        self.assertIsNotNone(generator)
    
    def test_advanced_generator_creation(self):
        """Test advanced generator creation"""
        generator = create_generator(
            mode="advanced",
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        self.assertIsNotNone(generator)
    
    def test_generator_with_middle_name(self):
        """Test generator with middle name"""
        generator = create_generator(
            mode="basic",
            first_name=self.test_first_name,
            last_name=self.test_last_name,
            middle_name=self.test_middle_name
        )
        self.assertIsNotNone(generator)
    
    def test_file_creation(self):
        """Test that files are created properly"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            output_file = tmp_file.name
        
        try:
            generator = create_generator(
                mode="basic",
                first_name=self.test_first_name,
                last_name=self.test_last_name
            )
            
            with StreamingFileWriter(output_file) as writer:
                word_count = 0
                for word in generator.generate_with_callback():
                    writer.add_word(word)
                    word_count += 1
                    if word_count >= 100:  # Limit for testing
                        break
            
            # Check file was created and has content
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertGreater(len(content), 0)
                
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        generator = create_generator(
            mode="basic",
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        
        stats = generator.get_statistics()
        self.assertIn("total_generated", stats)
        self.assertIn("generation_time", stats)

if __name__ == "__main__":
    unittest.main()