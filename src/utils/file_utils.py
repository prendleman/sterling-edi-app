"""
File utility functions for EDI processing.
Handles file operations, locking, and safe file handling.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def safe_move_file(source: str, destination: str, retries: int = 3, delay: float = 1.0) -> bool:
    """
    Safely move a file with retry logic.
    
    Args:
        source: Source file path
        destination: Destination file path
        retries: Number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        True if successful, False otherwise
    """
    source_path = Path(source)
    dest_path = Path(destination)
    
    # Create destination directory if needed
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    for attempt in range(retries):
        try:
            if source_path.exists():
                shutil.move(str(source_path), str(dest_path))
                logger.info(f"Moved {source} to {destination}")
                return True
            else:
                logger.warning(f"Source file not found: {source}")
                return False
        except (OSError, PermissionError) as e:
            if attempt < retries - 1:
                logger.warning(f"Move attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to move file after {retries} attempts: {e}")
                return False
    
    return False


def safe_copy_file(source: str, destination: str) -> bool:
    """
    Safely copy a file.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(source_path), str(dest_path))
        logger.info(f"Copied {source} to {destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy file: {e}")
        return False


def is_file_locked(filepath: str) -> bool:
    """
    Check if a file is locked (being used by another process).
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file appears to be locked
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return False
        
        # Try to open file in exclusive mode
        with open(path, 'r+b') as f:
            pass
        return False
    except (IOError, PermissionError):
        return True


def wait_for_file_ready(filepath: str, timeout: int = 30, check_interval: float = 0.5) -> bool:
    """
    Wait for a file to be ready (not locked and size stable).
    
    Args:
        filepath: Path to file
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        True if file is ready, False if timeout
    """
    path = Path(filepath)
    start_time = time.time()
    last_size = -1
    
    while time.time() - start_time < timeout:
        if not path.exists():
            time.sleep(check_interval)
            continue
        
        # Check if file is locked
        if is_file_locked(str(path)):
            time.sleep(check_interval)
            continue
        
        # Check if file size is stable
        current_size = path.stat().st_size
        if current_size == last_size and current_size > 0:
            return True
        
        last_size = current_size
        time.sleep(check_interval)
    
    logger.warning(f"File not ready after {timeout} seconds: {filepath}")
    return False


def get_file_extension(filepath: str) -> str:
    """
    Get file extension (lowercase, without dot).
    
    Args:
        filepath: Path to file
        
    Returns:
        File extension
    """
    return Path(filepath).suffix.lower().lstrip('.')


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

