import streamlit as st
import os
import time
import pandas as pd
from datetime import datetime
import sys
from collections import Counter
import base64

# Import our generators
from core.generator import create_generator
from core.stream_writer import StreamingFileWriter

# Page configuration
st.set_page_config(
    page_title="🔐 Advanced Wordlist Generator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Matrix Green Terminal Theme CSS
st.markdown("""
<style>
    /* Main background with subtle matrix grid */
    .stApp {
        background-color: #0a0a0a;
        background-image: 
            radial-gradient(#003300 0.5px, transparent 0.5px),
            radial-gradient(#003300 0.5px, #0a0a0a 0.5px);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        color: #00ff41;
        font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
        min-height: 100vh;
    }
    
    /* Content containers - ensure visibility */
    .main-container {
        background: rgba(5, 15, 5, 0.98);
        border-radius: 0px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 
            0 0 25px rgba(0, 255, 65, 0.4),
            inset 0 0 20px rgba(0, 255, 65, 0.1);
        border: 2px solid #00ff41;
        backdrop-filter: blur(5px);
        position: relative;
        z-index: 1;
    }
    
    /* Header styling - matrix green with strong glow */
    .main-header {
        font-size: 2.8rem;
        color: #00ff41;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-shadow: 
            0 0 10px #00ff41,
            0 0 20px #00ff41,
            0 0 30px #00ff41;
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        background: rgba(0, 25, 0, 0.9);
        padding: 1.5rem;
        border: 2px solid #00ff41;
        position: relative;
        animation: text-flicker 3s infinite alternate;
    }
    
    @keyframes text-flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            opacity: 1;
            text-shadow: 
                0 0 10px #00ff41,
                0 0 20px #00ff41,
                0 0 30px #00ff41;
        }
        20%, 24%, 55% {
            opacity: 0.9;
            text-shadow: 
                0 0 5px #00ff41,
                0 0 10px #00ff41;
        }
    }
    
    .main-subheader {
        text-align: center;
        color: #00ff88;
        margin-bottom: 2rem;
        font-size: 1.2rem;
        background: rgba(0, 30, 0, 0.8);
        padding: 1rem;
        border: 1px solid #00ff88;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    /* Section headers - high visibility */
    .section-header {
        color: #00ff41;
        border-bottom: 3px solid #00ff41;
        padding-bottom: 0.8rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        text-shadow: 0 0 10px #00ff41;
        font-family: 'Courier New', monospace;
        background: rgba(0, 30, 0, 0.7);
        padding: 1.2rem;
        margin-top: 1rem;
        font-size: 1.5rem;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }
    
    /* Form containers - ensure readability */
    .form-container {
        background: rgba(0, 35, 0, 0.9);
        border-radius: 0px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #00ff41;
        border-top: 1px solid #00aa00;
        border-right: 1px solid #00aa00;
        border-bottom: 1px solid #00aa00;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Buttons - matrix style */
    .stButton button {
        background: #002200;
        color: #00ff41 !important;
        border: 2px solid #00ff41;
        border-radius: 0px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        transition: all 0.3s ease;
        text-shadow: 0 0 8px #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
        position: relative;
        overflow: hidden;
        font-size: 1.1rem;
    }
    
    .stButton button:hover {
        background: #004400;
        box-shadow: 
            0 0 20px #00ff41,
            0 0 30px rgba(0, 255, 65, 0.6);
        transform: translateY(-2px);
        border-color: #00ff88;
    }
    
    /* Input fields - ensure visibility */
    .stTextInput input {
        background: #001a00 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 0px !important;
        padding: 0.8rem !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1.1rem !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3) inset;
    }
    
    .stTextInput input:focus {
        box-shadow: 
            0 0 15px #00ff41,
            0 0 25px rgba(0, 255, 65, 0.4) inset;
        background: #003300 !important;
        border-color: #00ff88 !important;
    }
    
    /* Select boxes */
    .stSelectbox select {
        background: #001a00 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 0px !important;
        padding: 0.8rem !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1.1rem !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3) inset;
    }
    
    /* Text areas */
    .stTextArea textarea {
        background: #001a00 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 0px !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1.1rem !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3) inset;
        line-height: 1.6;
    }
    
    /* Checkboxes and radio buttons */
    .stCheckbox, .stRadio {
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stCheckbox > div, .stRadio > div {
        background: rgba(0, 30, 0, 0.8) !important;
        border: 1px solid #00ff41 !important;
        border-radius: 0px !important;
        padding: 1rem !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) inset !important;
        color: #00ff41 !important;
    }
    
    /* Success boxes - high contrast */
    .success-box {
        background: rgba(0, 50, 0, 0.95);
        color: #00ff41;
        padding: 1.5rem;
        border-radius: 0px;
        border: 2px solid #00ff41;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.5);
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        line-height: 1.6;
        text-shadow: 0 0 5px #00ff41;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(0, 35, 20, 0.95);
        color: #00ff99;
        padding: 1.5rem;
        border-radius: 0px;
        border: 2px solid #00ff99;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(0, 255, 153, 0.4);
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        line-height: 1.6;
        text-shadow: 0 0 5px #00ff99;
    }
    
    /* Warning boxes */
    .warning-box {
        background: rgba(50, 50, 0, 0.95);
        color: #ffff00;
        padding: 1.5rem;
        border-radius: 0px;
        border: 2px solid #ffff00;
        margin: 1.5rem 0;
        box-shadow: 0 0 25px rgba(255, 255, 0, 0.4);
        font-family: 'Courier New', monospace;
        font-size: 1.1rem;
        line-height: 1.6;
        text-shadow: 0 0 5px #ffff00;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ff41, #00ff88);
        box-shadow: 0 0 15px #00ff41;
    }
    
    .stProgress > div > div {
        background: #001100;
        border: 2px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4) inset;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(0, 30, 0, 0.95);
        border-radius: 0px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        border-left: 5px solid #00ff41;
        border-top: 1px solid #00aa00;
        border-right: 1px solid #00aa00;
        border-bottom: 1px solid #00aa00;
        color: #00ff41;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
        position: relative;
        text-shadow: 0 0 5px #00ff41;
    }
    
    /* Vertical divider */
    .vertical-divider {
        border-left: 3px solid #00ff41;
        height: 100%;
        margin: 0 2rem;
        box-shadow: 0 0 15px #00ff41;
    }
    
    /* Dataframes - readable matrix style */
    .dataframe {
        background: #001a00 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        font-family: 'Courier New', monospace !important;
    }
    
    .dataframe th {
        background: #003300 !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        font-weight: bold;
        text-shadow: 0 0 8px #00ff41;
        padding: 1rem !important;
        font-size: 1.1rem;
    }
    
    .dataframe td {
        background: #001a00 !important;
        color: #00ff41 !important;
        border: 1px solid #005500 !important;
        padding: 0.8rem !important;
        font-size: 1rem;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: rgba(0, 30, 0, 0.9) !important;
        border: 2px dashed #00ff41 !important;
        border-radius: 0px !important;
        color: #00ff41 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(0, 40, 0, 0.95) !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold;
        text-shadow: 0 0 8px #00ff41;
        font-size: 1.1rem;
    }
    
    .streamlit-expanderContent {
        background: rgba(0, 25, 0, 0.9) !important;
        border: 1px solid #003300 !important;
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #001100;
        border-bottom: 3px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #00cc33;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00ff41 !important;
        background: rgba(0, 255, 65, 0.15);
        text-shadow: 0 0 10px #00ff41;
        border-bottom: 3px solid #00ff41;
    }
    
    /* Markdown text - ensure readability */
    .stMarkdown {
        color: #00ff41;
        font-family: 'Courier New', monospace;
        line-height: 1.7;
        font-size: 1.05rem;
    }
    
    .stMarkdown strong {
        color: #00ff88;
        text-shadow: 0 0 8px #00ff88;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #001100 !important;
        border: 2px solid #00ff41 !important;
        border-radius: 0px !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1rem;
    }
    
    /* Ensure all text is visible with proper contrast */
    * {
        text-shadow: 0 0 2px rgba(0, 255, 65, 0.7);
    }
    
    /* Labels and titles */
    label {
        color: #00ff88 !important;
        font-weight: bold !important;
        text-shadow: 0 0 5px #00ff88;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbm6i {
        background: #0a0a0a !important;
        border-right: 2px solid #00ff41;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.3);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #001100;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00ff41;
        box-shadow: 0 0 15px #00ff41;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00ff88;
    }
    
    /* Error messages */
    .stAlert {
        background: rgba(50, 0, 0, 0.95) !important;
        border: 2px solid #ff4444 !important;
        color: #ff4444 !important;
        text-shadow: 0 0 8px #ff4444;
    }
</style>
""", unsafe_allow_html=True)

def ensure_wordlists_folder():
    """Create wordlists folder if it doesn't exist"""
    if not os.path.exists("wordlists"):
        os.makedirs("wordlists")

def generate_filename(first_name, last_name, mode):
    """Generate a filename with timestamp and mode"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"wordlists/{mode}_wordlist_{first_name}_{last_name}_{timestamp}.txt"

def clear_all():
    """Clear the entire page by resetting session state and rerunning"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def exit_app():
    """Exit the application"""
    st.markdown("""
    <div style="background: rgba(50, 0, 0, 0.95); color: #ff4444; padding: 1.5rem; border-radius: 0px; border: 2px solid #ff4444; margin: 1.5rem 0; box-shadow: 0 0 25px rgba(255, 68, 68, 0.4);">
        <h3 style='color: #ff4444; text-shadow: 0 0 10px #ff4444;'>🚪 Exiting Application</h3>
        <p style='color: #ff4444;'>Thank you for using Wordlist Generator!</p>
        <p style='color: #ff4444;'>This window will close automatically.</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    sys.exit(0)

def analyze_duplicates(uploaded_file):
    """Analyze uploaded wordlist for exact duplicates"""
    try:
        # Read the uploaded file
        content = uploaded_file.getvalue().decode("utf-8")
        lines = content.split('\n')
        
        # Count exact duplicates (case-sensitive, exact match)
        word_counts = Counter()
        total_words = 0
        unique_words = set()
        
        for line in lines:
            word = line.strip()
            if word:  # Only process non-empty lines
                word_counts[word] += 1
                unique_words.add(word)
                total_words += 1
        
        # Find duplicates (words with count > 1)
        duplicates = {word: count for word, count in word_counts.items() if count > 1}
        
        # Calculate statistics
        stats = {
            'total_words': total_words,
            'unique_words': len(unique_words),
            'duplicate_words': len(duplicates),
            'total_duplicates': sum(duplicates.values()) - len(duplicates),  # Total extra copies
            'duplicate_percentage': (len(duplicates) / len(unique_words)) * 100 if unique_words else 0
        }
        
        return duplicates, stats, None
        
    except Exception as e:
        return None, None, str(e)

def main():
    # Main container
    with st.container():
        st.markdown('<h1 class="main-header">🔐 Advanced Wordlist Generator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="main-subheader">Generate custom wordlists & Analyze duplicates in one place</p>', unsafe_allow_html=True)
        
        # Ensure wordlists folder exists
        ensure_wordlists_folder()
        
        # Create two main columns with a divider
        col_left, col_divider, col_right = st.columns([5, 0.2, 5])
        
        with col_left:
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            # Generate Wordlist Section
            st.markdown('<h2 class="section-header">🚀 Generate Wordlist</h2>', unsafe_allow_html=True)
            
            # Personal Info Section
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('**👤 Personal Information**')
            col_name1, col_name2, col_name3 = st.columns(3)
            with col_name1:
                first_name = st.text_input("First Name *", placeholder="John", key="first_name", help="Required field")
            with col_name2:
                middle_name = st.text_input("Middle Name", placeholder="Abraham", key="middle_name", help="Optional")
            with col_name3:
                last_name = st.text_input("Last Name *", placeholder="Doe", key="last_name", help="Required field")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Configuration Options (Compact)
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('**⚙️ Configuration Options**')
            mode = st.radio(
                "Generation Mode:",
                ["basic", "advanced"],
                format_func=lambda x: "🟢 Basic (Memory Efficient)" if x == "basic" else "🔴 Advanced (Comprehensive)",
                horizontal=True,
                key="mode"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Settings (Compact)
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('**🔧 Settings**')
            col_set1, col_set2 = st.columns(2)
            with col_set1:
                min_length = st.slider("Minimum Length", 1, 10, 3, key="min_length")
            with col_set2:
                max_length = st.slider("Maximum Length", 5, 30, 12, key="max_length")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Patterns (Compact Grid)
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('**🎭 Patterns**')
            col_pat1, col_pat2, col_pat3, col_pat4, col_pat5 = st.columns(5)
            with col_pat1:
                enable_leet = st.checkbox("Leet", value=True, key="enable_leet", help="p@ssw0rd")
            with col_pat2:
                enable_capitals = st.checkbox("Capital", value=True, key="enable_capitals", help="PASSWORD")
            with col_pat3:
                append_numbers = st.checkbox("Append", value=True, key="append_numbers", help="password123")
            with col_pat4:
                prepend_numbers = st.checkbox("Prepend", value=True, key="prepend_numbers", help="123password")
            with col_pat5:
                special_chars = st.checkbox("Special", value=True, key="special_chars", help="!password")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate Button
            if st.button("🎯 Generate Wordlist", type="primary", use_container_width=True, key="generate_btn"):
                if not first_name or not last_name:
                    st.error("❌ Please provide both First Name and Last Name")
                else:
                    # Initialize progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    preview_text = st.empty()
                    stats_placeholder = st.empty()
                    warning_text = st.empty()
                    
                    generated_words = []
                    start_time = time.time()
                    MAX_GENERATION_TIME = 120  # 2 minutes max
                    
                    def should_continue():
                        return time.time() - start_time < MAX_GENERATION_TIME
                    
                    def update_callback(word, count, duplicates):
                        if not should_continue():
                            warning_text.warning("⚠️ Generation taking too long. Consider using Basic mode or reducing patterns.")
                            return
                            
                        generated_words.append(word)
                        
                        update_interval = 50 if mode == "basic" else 20
                        if count % update_interval == 0:
                            expected_words = 1000 if mode == "basic" else 5000
                            progress = min(count / expected_words, 1.0)
                            progress_bar.progress(progress)
                            
                            status_text.text(f"🔄 Generating... {count} words ({duplicates} duplicates prevented)")
                            
                            # Show preview
                            preview_count = 10
                            if len(generated_words) > preview_count:
                                preview_content = "\n".join(generated_words[-preview_count:])
                            else:
                                preview_content = "\n".join(generated_words)
                            
                            with preview_text.container():
                                st.markdown(f"**Live Preview (Last {preview_count} words):**")
                                st.code(preview_content)
                            
                            # Update stats
                            current_time = time.time()
                            elapsed = current_time - start_time
                            wps = count / elapsed if elapsed > 0 else 0
                            
                            with stats_placeholder.container():
                                cols = st.columns(4)
                                cols[0].metric("Words", f"{count}")
                                cols[1].metric("Duplicates", f"{duplicates}")
                                cols[2].metric("Time", f"{elapsed:.1f}s")
                                cols[3].metric("Speed", f"{wps:.0f}/s")
                    
                    try:
                        generator = create_generator(
                            mode=mode,
                            first_name=first_name,
                            last_name=last_name,
                            middle_name=middle_name if middle_name else None,
                            max_length=max_length,
                            min_length=min_length,
                            enable_leet=enable_leet,
                            enable_capitals=enable_capitals,
                            append_numbers=append_numbers,
                            prepend_numbers=prepend_numbers,
                            special_chars=special_chars
                        )
                        
                        output_file = generate_filename(first_name, last_name, mode)
                        
                        with StreamingFileWriter(output_file) as writer:
                            for word in generator.generate_with_callback(update_callback):
                                if not should_continue():
                                    warning_text.warning("⏰ Generation stopped due to timeout")
                                    break
                                writer.add_word(word)
                        
                        stats = generator.get_statistics()
                        progress_bar.progress(1.0)
                        
                        st.success(f"✅ Generated {stats['total_generated']:,} words in {stats['generation_time']:.2f}s")
                        
                        # Download section
                        with open(output_file, 'r') as f:
                            st.download_button(
                                "💾 Download Wordlist",
                                f.read(),
                                file_name=os.path.basename(output_file),
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            # Bottom divider line and action buttons
            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
                    clear_all()
            with col_btn2:
                if st.button("🚪 Exit App", use_container_width=True, type="secondary"):
                    exit_app()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_divider:
            # Vertical divider
            st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            # Analyze Duplicates Section
            st.markdown('<h2 class="section-header">🔍 Analyze Duplicates</h2>', unsafe_allow_html=True)
            
            # File upload section
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown("**📁 Drop Your Wordlist File Here**")
            uploaded_file = st.file_uploader(
                "Choose a wordlist file",
                type=['txt'],
                help="Upload a .txt file with one word per line",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.info(f"**📄 File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
                
                # Analyze button
                if st.button("🔎 Analyze for Duplicates", type="primary", use_container_width=True, key="analyze_btn"):
                    with st.spinner("Analyzing wordlist for duplicates..."):
                        duplicates, stats, error = analyze_duplicates(uploaded_file)
                        
                        if error:
                            st.error(f"❌ Error analyzing file: {error}")
                        else:
                            # Display statistics
                            st.markdown("**📊 Analysis Summary**")
                            
                            cols = st.columns(4)
                            cols[0].metric("Total Words", f"{stats['total_words']:,}")
                            cols[1].metric("Unique Words", f"{stats['unique_words']:,}")
                            cols[2].metric("Duplicate Words", f"{stats['duplicate_words']:,}")
                            cols[3].metric("Duplicate Rate", f"{stats['duplicate_percentage']:.1f}%")
                            
                            # Display duplicate details
                            if duplicates:
                                st.markdown("**📋 Duplicate Words Found**")
                                
                                # Create sorted list of duplicates
                                sorted_duplicates = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
                                
                                # Display in a table
                                duplicate_data = []
                                for word, count in sorted_duplicates:
                                    duplicate_data.append({
                                        "Word": word,
                                        "Count": count,
                                        "Extra Copies": count - 1
                                    })
                                
                                df_duplicates = pd.DataFrame(duplicate_data)
                                st.dataframe(
                                    df_duplicates,
                                    use_container_width=True,
                                    height=300
                                )
                                
                                # Show top duplicates chart
                                st.markdown("**📈 Top Duplicates**")
                                top_10 = sorted_duplicates[:10]
                                chart_data = pd.DataFrame({
                                    'Word': [item[0] for item in top_10],
                                    'Count': [item[1] for item in top_10]
                                })
                                st.bar_chart(chart_data.set_index('Word'))
                                
                                # Download report
                                st.markdown("**📥 Download Analysis Report**")
                                report_content = f"""Wordlist Duplicate Analysis Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
File: {uploaded_file.name}

SUMMARY:
Total Words: {stats['total_words']:,}
Unique Words: {stats['unique_words']:,}
Duplicate Words: {stats['duplicate_words']:,}
Duplicate Rate: {stats['duplicate_percentage']:.1f}%

DUPLICATE WORDS:
"""
                                for word, count in sorted_duplicates:
                                    report_content += f"{word} -> {count} times\n"
                                
                                st.download_button(
                                    "📄 Download Duplicate Report",
                                    report_content,
                                    file_name=f"duplicate_report_{uploaded_file.name}.txt",
                                    use_container_width=True
                                )
                                
                            else:
                                st.success(f"✅ No duplicates found! All {stats['unique_words']} words are unique.")
            else:
                # Instructions when no file is uploaded
                st.markdown("""
                <div class="info-box">
                    <h4>📋 How to Analyze Duplicates</h4>
                    <ol>
                        <li><strong>Upload a wordlist file</strong> (.txt format, one word per line)</li>
                        <li><strong>Click "Analyze for Duplicates"</strong> to process the file</li>
                        <li><strong>View the results</strong> showing exact duplicate counts</li>
                        <li><strong>Download the report</strong> for your records</li>
                    </ol>
                    
                    <p><strong>Note:</strong> Analysis is case-sensitive. "Password" and "password" are considered different words.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Bottom divider line and action buttons (Right side)
            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ Clear All ", use_container_width=True, type="secondary", key="clear_right"):
                    clear_all()
            with col_btn2:
                if st.button("🚪 Exit App ", use_container_width=True, type="secondary", key="exit_right"):
                    exit_app()
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()