"""
Progress tracking utilities for the podcast AI pipeline.
"""

from contextlib import contextmanager
from typing import Optional

from tqdm import tqdm


class ProgressTracker:
    """Enhanced progress tracking with context management."""

    def __init__(self):
        self.current_progress = None

    @contextmanager
    def track(self, description: str, total: Optional[int] = None, **kwargs):
        """Context manager for progress tracking."""
        progress_bar = tqdm(desc=description, total=total, **kwargs)
        self.current_progress = progress_bar
        try:
            yield progress_bar
        finally:
            progress_bar.close()
            self.current_progress = None

    def update_description(self, description: str):
        """Update the description of the current progress bar."""
        if self.current_progress:
            self.current_progress.set_description(description)

    def set_postfix(self, **kwargs):
        """Set postfix information for the current progress bar."""
        if self.current_progress:
            self.current_progress.set_postfix(**kwargs)


def create_progress_bar(
    description: str, total: Optional[int] = None, unit: str = "it", leave: bool = True
) -> tqdm:
    """Create a standardized progress bar."""
    return tqdm(
        desc=description,
        total=total,
        unit=unit,
        leave=leave,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    )


def show_step_progress(step_name: str, current: int, total: int):
    """Show simple step progress without a full progress bar."""
    print(f"🔄 {step_name} ({current}/{total})")


def show_completion_message(task_name: str, duration_seconds: float = None):
    """Show a completion message with optional duration."""
    if duration_seconds:
        print(f"✅ {task_name} complete! ({duration_seconds:.1f}s)")
    else:
        print(f"✅ {task_name} complete!")
