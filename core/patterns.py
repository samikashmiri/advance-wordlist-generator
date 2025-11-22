from typing import Set, Generator
import itertools

class BasicPatternGenerator:
    """Efficient Basic Pattern Generator"""
    
    def __init__(self):
        self.leet_map = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$']
        }
        
        self.common_numbers = ['1', '12', '123', '1234', '007', '69', '2024', '2023']
        self.special_chars = ['!', '@', '#', '$']
    
    def smart_leet_transform(self, word: str) -> Generator[str, None, None]:
        """Smart leet transform without explosion"""
        yield word  # Original
        
        # Single substitution passes (most effective ones)
        if 'a' in word.lower():
            yield word.replace('a', '4').replace('A', '4')
            yield word.replace('a', '@').replace('A', '@')
        if 'e' in word.lower():
            yield word.replace('e', '3').replace('E', '3')
        if 'i' in word.lower():
            yield word.replace('i', '1').replace('I', '1')
        if 'o' in word.lower():
            yield word.replace('o', '0').replace('O', '0')
        if 's' in word.lower():
            yield word.replace('s', '5').replace('S', '5')
            yield word.replace('s', '$').replace('S', '$')
    
    def smart_number_append(self, word: str) -> Generator[str, None, None]:
        """Smart number appending"""
        for num in self.common_numbers:
            if len(word + num) <= self._get_max_length():
                yield word + num
        
        # Limited single digits
        for i in range(10):
            yield word + str(i)
    
    def smart_number_prepend(self, word: str) -> Generator[str, None, None]:
        """Smart number prepending"""
        for num in self.common_numbers[:5]:  # Only first 5
            if len(num + word) <= self._get_max_length():
                yield num + word
        
        for i in range(5):  # Only 0-4
            yield str(i) + word
    
    def smart_special_chars(self, word: str) -> Generator[str, None, None]:
        """Smart special characters"""
        for char in self.special_chars:
            if len(char + word) <= self._get_max_length():
                yield char + word
            if len(word + char) <= self._get_max_length():
                yield word + char
    
    def _get_max_length(self):
        return 20

class AdvancedPatternGenerator:
    """Optimized Advanced Pattern Generator"""
    
    def __init__(self):
        self.leet_map = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7']
        }
        
        self.special_chars = ['!', '@', '#', '$', '%', '&', '*']
        self.common_numbers = ['1', '12', '123', '1234', '12345', '007', '69', '420', '777']
        self.years = ['2024', '2023', '2022', '2021', '2020']
    
    def optimized_leet_transform(self, word: str) -> Set[str]:
        """Optimized leet transform with limits"""
        results = set()
        results.add(word)
        
        # Single pass with common substitutions
        substitutions = [
            ('a', '4'), ('a', '@'), ('e', '3'), ('i', '1'),
            ('i', '!'), ('o', '0'), ('s', '5'), ('s', '$'), ('t', '7')
        ]
        
        for original, replacement in substitutions:
            if original in word.lower():
                # Replace all occurrences
                new_word = word.lower().replace(original, replacement)
                results.add(new_word)
                # Also try with original case
                new_word_mixed = ''
                for char in word:
                    if char.lower() == original:
                        new_word_mixed += replacement
                    else:
                        new_word_mixed += char
                results.add(new_word_mixed)
        
        return results
    
    def optimized_capitalization(self, word: str) -> Set[str]:
        """Optimized capitalization patterns"""
        patterns = set()
        
        patterns.add(word.upper())
        patterns.add(word.capitalize())
        
        if len(word) > 3:
            patterns.add(word[0].upper() + word[1:].lower())
        
        # Camel case for separated words
        for separator in [' ', '-', '_', '.']:
            if separator in word:
                parts = word.split(separator)
                camel_case = parts[0] + ''.join(part.capitalize() for part in parts[1:])
                patterns.add(camel_case)
                break
        
        return patterns
    
    def optimized_number_append(self, word: str) -> Set[str]:
        """Optimized number appending"""
        results = set()
        
        for num in self.common_numbers:
            if len(word + num) <= 20:
                results.add(word + num)
        
        for year in self.years:
            if len(word + year) <= 20:
                results.add(word + year)
        
        # Limited number ranges
        for i in range(10):
            results.add(word + str(i))
        
        for i in range(10, 100, 10):  # 10, 20, 30, ..., 90
            results.add(word + str(i))
        
        return results
    
    def optimized_number_prepend(self, word: str) -> Set[str]:
        """Optimized number prepending"""
        results = set()
        
        for num in self.common_numbers[:8]:  # Limited set
            if len(num + word) <= 20:
                results.add(num + word)
        
        for year in self.years[:3]:  # Only recent years
            if len(year + word) <= 20:
                results.add(year + word)
        
        for i in range(10):
            results.add(str(i) + word)
        
        return results
    
    def optimized_special_chars(self, word: str) -> Set[str]:
        """Optimized special characters"""
        results = set()
        
        for char in self.special_chars:
            results.add(char + word)
            results.add(word + char)
            if char in ['!', '@', '#']:  # Only wrap common ones
                results.add(char + word + char)
        
        # Limited combinations
        for char1 in self.special_chars[:2]:
            for char2 in self.special_chars[:2]:
                results.add(char1 + word + char2)
        
        return results