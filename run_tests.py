#!/usr/bin/env python3
"""
Wordlist Generator Test Runner
Compatible with Windows, Linux, and Mac
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all tests in the tests directory"""
    print("🧪 Starting Wordlist Generator Test Suite...")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Create tests directory if it doesn't exist
    if not os.path.exists(start_dir):
        os.makedirs(start_dir)
        print(f"📁 Created tests directory: {start_dir}")
    
    try:
        suite = loader.discover(start_dir, pattern='test_*.py')
    except Exception as e:
        print(f"❌ Error discovering tests: {e}")
        print("💡 Creating sample test files...")
        create_sample_tests()
        suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚨 Errors: {len(result.errors)}")
    
    # Print failures and errors if any
    if result.failures:
        print("\n📋 FAILURES:")
        for test, traceback in result.failures:
            print(f"   ❌ {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   💥 {test}: {traceback.splitlines()[-1]}")
    
    return result.wasSuccessful()

def create_sample_tests():
    """Create sample test files if tests directory is empty"""
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Create __init__.py
    init_file = os.path.join(tests_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('# Tests package\n')
    
    # Create basic test file
    test_file = os.path.join(tests_dir, 'test_basic.py')
    with open(test_file, 'w') as f:
        f.write('''
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.generator import create_generator

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests"""
    
    def test_generator_creation(self):
        """Test that generators can be created"""
        # Test basic generator
        basic_gen = create_generator(
            mode="basic",
            first_name="john",
            last_name="doe"
        )
        self.assertIsNotNone(basic_gen)
        self.assertGreater(len(basic_gen.base_words), 0)
        
        # Test advanced generator
        advanced_gen = create_generator(
            mode="advanced", 
            first_name="john",
            last_name="doe"
        )
        self.assertIsNotNone(advanced_gen)
        self.assertGreater(len(advanced_gen.base_words), 0)
    
    def test_name_combinations(self):
        """Test name combination generation"""
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
        generator = create_generator(
            mode="basic",
            first_name="test",
            last_name="user"
        )
        
        stats = generator.get_statistics()
        self.assertIn("base_combinations", stats)
        self.assertIn("total_generated", stats)
        self.assertIn("generation_time", stats)

if __name__ == '__main__':
    unittest.main()
''')
    
    print("✅ Created sample test files")

def run_performance_benchmark():
    """Run performance benchmarks"""
    print("\n" + "=" * 60)
    print("🚀 PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    try:
        from core.generator import create_generator, benchmark_generator
        
        # Test basic generator performance
        print("Testing Basic Generator...")
        basic_gen = create_generator(
            mode="basic",
            first_name="john",
            last_name="doe",
            max_length=12,
            min_length=3
        )
        
        basic_results = benchmark_generator(basic_gen, sample_size=1000)
        print(f"✅ Basic Generator: {basic_results['words_per_second']:.1f} words/sec")
        
        # Test advanced generator performance  
        print("Testing Advanced Generator...")
        advanced_gen = create_generator(
            mode="advanced",
            first_name="john", 
            last_name="doe",
            max_length=12,
            min_length=3
        )
        
        advanced_results = benchmark_generator(advanced_gen, sample_size=1000)
        print(f"✅ Advanced Generator: {advanced_results['words_per_second']:.1f} words/sec")
        
        # Compare results
        print("\n📊 PERFORMANCE COMPARISON:")
        print(f"   Basic Mode: {basic_results['words_per_second']:.1f} words/sec")
        print(f"   Advanced Mode: {advanced_results['words_per_second']:.1f} words/sec")
        print(f"   Memory Efficiency: {basic_results['efficiency_rating']}")
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")

def check_system_requirements():
    """Check system requirements and dependencies"""
    print("\n" + "=" * 60)
    print("🔧 SYSTEM CHECK")
    print("=" * 60)
    
    requirements = {
        "Python 3.6+": sys.version_info >= (3, 6),
        "Core Modules": all(
            hasattr(__import__('unittest'), attr) 
            for attr in ['TestLoader', 'TextTestRunner']
        )
    }
    
    # Check for optional dependencies
    try:
        import psutil
        requirements["psutil"] = True
    except ImportError:
        requirements["psutil"] = False
    
    try:
        import pandas
        requirements["pandas"] = True
    except ImportError:
        requirements["pandas"] = False
    
    # Print results
    all_met = True
    for requirement, met in requirements.items():
        status = "✅" if met else "❌"
        print(f"   {status} {requirement}")
        if not met:
            all_met = False
    
    return all_met

if __name__ == "__main__":
    start_time = time.time()
    
    # System check
    if not check_system_requirements():
        print("\n⚠️  Some optional dependencies are missing.")
        print("💡 Install them with: pip install psutil pandas")
    
    # Run tests
    success = run_all_tests()
    
    # Run performance benchmark if tests passed
    if success:
        run_performance_benchmark()
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    if success:
        print(f"🎉 ALL TESTS PASSED! Total time: {total_time:.2f}s")
        sys.exit(0)
    else:
        print(f"💥 SOME TESTS FAILED! Total time: {total_time:.2f}s")
        sys.exit(1)