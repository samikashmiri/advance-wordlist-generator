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

# Blue Gradient Theme CSS
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Content containers */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-subheader {
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Section headers */
    .section-header {
        color: #495057;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Form containers */
    .form-container {
        background: rgba(248, 249, 250, 0.8);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Success boxes */
    .success-box {
        background: linear-gradient(45deg, #d4edda, #c3e6cb);
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(45deg, #d1ecf1, #bee5eb);
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    
    /* Warning boxes */
    .warning-box {
        background: linear-gradient(45deg, #fff3cd, #ffeaa7);
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    /* Vertical divider */
    .vertical-divider {
        border-left: 2px solid #dee2e6;
        height: 100%;
        margin: 0 2rem;
    }
    
    /* Compact form elements */
    .compact-input {
        margin-bottom: 0.5rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
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
    <div style="background: linear-gradient(45deg, #f8d7da, #f5c6cb); color: #721c24; padding: 1rem; border-radius: 8px; border: 1px solid #f5c6cb; margin: 1rem 0;">
        <h3>🚪 Exiting Application</h3>
        <p>Thank you for using Wordlist Generator!</p>
        <p>This window will close automatically.</p>
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