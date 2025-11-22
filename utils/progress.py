import time
from typing import Callable, Dict, Any
import streamlit as st

class ProgressNotifier:
    """Advanced progress notification system"""
    
    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.phase = "Initializing"
        
    def update_progress(self, step: int, phase: str, details: Dict[str, Any] = None):
        """Update progress with detailed information"""
        self.current_step = step
        self.phase = phase
        
        progress = min(step / self.total_steps, 1.0)
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calculate ETA
        if step > 0:
            steps_per_second = step / elapsed
            remaining_steps = self.total_steps - step
            eta = remaining_steps / steps_per_second if steps_per_second > 0 else 0
        else:
            eta = 0
        
        # Build progress message
        message = f"**{phase}** - {step}/{self.total_steps} steps"
        if details:
            message += f" | {self._format_details(details)}"
        
        if eta > 0:
            message += f" | ETA: {self._format_time(eta)}"
        
        return progress, message
    
    def _format_details(self, details: Dict[str, Any]) -> str:
        """Format details for display"""
        parts = []
        for key, value in details.items():
            if isinstance(value, int) and value > 1000:
                parts.append(f"{key}: {value:,}")
            else:
                parts.append(f"{key}: {value}")
        return " | ".join(parts)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def complete(self):
        """Mark progress as complete"""
        total_time = time.time() - self.start_time
        return f"✅ Completed in {self._format_time(total_time)}"

class StreamlitProgressManager:
    """Manage progress display in Streamlit"""
    
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        self.details_text = None
        
    def initialize_display(self):
        """Initialize progress display elements"""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.details_text = st.empty()
    
    def update_display(self, progress: float, message: str, details: str = ""):
        """Update progress display"""
        if self.progress_bar:
            self.progress_bar.progress(progress)
        if self.status_text:
            self.status_text.markdown(f"**Progress:** {message}")
        if self.details_text and details:
            self.details_text.markdown(f"*{details}*")