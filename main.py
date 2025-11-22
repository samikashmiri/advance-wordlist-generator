#!/usr/bin/env python3
import argparse
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.generator import create_generator
from core.stream_writer import StreamingFileWriter
from utils.file_handler import FileHandler

def main():
    parser = argparse.ArgumentParser(description='Dual-Mode Wordlist Generator')
    parser.add_argument('--first-name', required=True, help='First name')
    parser.add_argument('--last-name', required=True, help='Last name')
    parser.add_argument('--middle-name', help='Middle name (optional)')
    parser.add_argument('--mode', choices=['basic', 'advanced'], default='basic', help='Generation mode')
    parser.add_argument('-o', '--output', help='Output file (auto-generated if not provided)')
    parser.add_argument('--max-length', type=int, default=12, help='Max word length')
    parser.add_argument('--min-length', type=int, default=3, help='Min word length')
    parser.add_argument('--no-leet', action='store_true', help='Disable leet speak')
    parser.add_argument('--no-capitals', action='store_true', help='Disable capitalization')
    parser.add_argument('--no-append-numbers', action='store_true', help='Disable number appending')
    parser.add_argument('--no-prepend-numbers', action='store_true', help='Disable number prepending')
    parser.add_argument('--no-special-chars', action='store_true', help='Disable special characters')
    parser.add_argument('--show-progress', action='store_true', help='Show generation progress')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        args.output = f"wordlists/{args.mode}_wordlist_{args.first_name}_{args.last_name}_{int(datetime.now().timestamp())}.txt"
    
    # Initialize generator
    generator = create_generator(
        mode=args.mode,
        first_name=args.first_name,
        last_name=args.last_name,
        middle_name=args.middle_name,
        max_length=args.max_length,
        min_length=args.min_length,
        enable_leet=not args.no_leet,
        enable_capitals=not args.no_capitals,
        append_numbers=not args.no_append_numbers,
        prepend_numbers=not args.no_prepend_numbers,
        special_chars=not args.no_special_chars
    )
    
    # Progress callback
    def progress_callback(word, count, duplicates):
        if args.show_progress and count % 100 == 0:
            print(f"Generated {count} words, prevented {duplicates} duplicates...", end='\r')
    
    # Generate wordlist
    word_count = 0
    duplicate_count = 0
    print(f"🚀 Starting {args.mode.upper()} mode wordlist generation...")
    start_time = datetime.now()
    
    with StreamingFileWriter(args.output) as writer:
        for word in generator.generate_with_callback(progress_callback):
            writer.add_word(word)
            word_count += 1
    
    end_time = datetime.now()
    generation_time = (end_time - start_time).total_seconds()
    
    # Display results
    stats = generator.get_statistics()
    print("\n" + "="*60)
    print(f"✅ {args.mode.upper()} MODE GENERATION COMPLETE")
    print("="*60)
    print(f"📁 File: {args.output}")
    print(f"🔢 Words generated: {word_count:,}")
    print(f"🚫 Duplicates prevented: {stats['duplicates_prevented']:,}")
    print(f"⏱️  Time taken: {generation_time:.2f} seconds")
    print(f"⚡ Speed: {stats['words_per_second']:.0f} words/second")
    print(f"🎯 Base combinations: {stats['base_combinations']}")
    print("="*60)

if __name__ == "__main__":
    main()