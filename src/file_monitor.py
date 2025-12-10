"""
File Monitor
Monitors directories for new EDI files and triggers processing.
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Callable, List, Optional, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .utils.file_utils import wait_for_file_ready, safe_move_file

logger = logging.getLogger(__name__)


class EDIFileHandler(FileSystemEventHandler):
    """Handler for EDI file system events."""
    
    def __init__(self, 
                 callback: Callable[[str], None],
                 file_extensions: List[str] = None,
                 stable_delay: float = 2.0):
        """
        Initialize file handler.
        
        Args:
            callback: Function to call when file is ready
            file_extensions: List of file extensions to monitor (None = all)
            stable_delay: Delay to wait for file to be stable (seconds)
        """
        super().__init__()
        self.callback = callback
        self.file_extensions = file_extensions or ['.edi', '.x12', '.edifact', '.txt']
        self.stable_delay = stable_delay
        self.processing_files = set()
        self.file_timers = {}
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation event."""
        if event.is_directory:
            return
        
        filepath = event.src_path
        if self._should_process(filepath):
            logger.info(f"New file detected: {filepath}")
            # Wait a bit for file to be fully written
            threading.Timer(self.stable_delay, self._process_file, args=(filepath,)).start()
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification event."""
        if event.is_directory:
            return
        
        filepath = event.src_path
        if self._should_process(filepath) and filepath not in self.processing_files:
            # Cancel previous timer if exists
            if filepath in self.file_timers:
                self.file_timers[filepath].cancel()
            
            # Start new timer
            timer = threading.Timer(self.stable_delay, self._process_file, args=(filepath,))
            self.file_timers[filepath] = timer
            timer.start()
    
    def _should_process(self, filepath: str) -> bool:
        """Check if file should be processed."""
        if filepath in self.processing_files:
            return False
        
        ext = Path(filepath).suffix.lower()
        return ext in self.file_extensions or not self.file_extensions
    
    def _process_file(self, filepath: str):
        """Process file after it's stable."""
        if filepath in self.processing_files:
            return
        
        # Check if file is ready
        if not wait_for_file_ready(filepath, timeout=30):
            logger.warning(f"File not ready after timeout: {filepath}")
            return
        
        self.processing_files.add(filepath)
        try:
            logger.info(f"Processing file: {filepath}")
            self.callback(filepath)
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")
        finally:
            self.processing_files.discard(filepath)
            if filepath in self.file_timers:
                del self.file_timers[filepath]


class FileMonitor:
    """Monitors directories for new EDI files."""
    
    def __init__(self, 
                 watch_directories: List[str],
                 callback: Callable[[str], None],
                 file_extensions: List[str] = None,
                 recursive: bool = True):
        """
        Initialize file monitor.
        
        Args:
            watch_directories: List of directories to monitor
            callback: Function to call when file is detected
            file_extensions: List of file extensions to monitor
            recursive: Whether to monitor subdirectories
        """
        self.watch_directories = [Path(d) for d in watch_directories]
        self.callback = callback
        self.file_extensions = file_extensions
        self.recursive = recursive
        self.observer = Observer()
        self.handlers = []
        self.is_running = False
    
    def start(self):
        """Start monitoring directories."""
        if self.is_running:
            logger.warning("File monitor is already running")
            return
        
        for directory in self.watch_directories:
            if not directory.exists():
                logger.warning(f"Watch directory does not exist: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created watch directory: {directory}")
            
            handler = EDIFileHandler(
                callback=self.callback,
                file_extensions=self.file_extensions
            )
            self.handlers.append(handler)
            
            self.observer.schedule(
                handler,
                str(directory),
                recursive=self.recursive
            )
            logger.info(f"Monitoring directory: {directory} (recursive={self.recursive})")
        
        self.observer.start()
        self.is_running = True
        logger.info("File monitor started")
    
    def stop(self):
        """Stop monitoring directories."""
        if not self.is_running:
            return
        
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        logger.info("File monitor stopped")
    
    def is_alive(self) -> bool:
        """Check if monitor is running."""
        return self.is_running and self.observer.is_alive()


class PollingFileMonitor:
    """
    Alternative file monitor using polling (for systems without watchdog support).
    """
    
    def __init__(self,
                 watch_directories: List[str],
                 callback: Callable[[str], None],
                 file_extensions: List[str] = None,
                 poll_interval: float = 5.0):
        """
        Initialize polling file monitor.
        
        Args:
            watch_directories: List of directories to monitor
            callback: Function to call when file is detected
            file_extensions: List of file extensions to monitor
            poll_interval: Polling interval in seconds
        """
        self.watch_directories = [Path(d) for d in watch_directories]
        self.callback = callback
        self.file_extensions = file_extensions or ['.edi', '.x12', '.edifact', '.txt']
        self.poll_interval = poll_interval
        self.known_files = set()
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start polling for files."""
        if self.is_running:
            logger.warning("Polling monitor is already running")
            return
        
        # Initialize known files
        for directory in self.watch_directories:
            if directory.exists():
                for filepath in directory.rglob('*'):
                    if filepath.is_file() and self._should_process(filepath):
                        self.known_files.add(str(filepath))
        
        self.is_running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("Polling file monitor started")
    
    def stop(self):
        """Stop polling for files."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("Polling file monitor stopped")
    
    def _poll_loop(self):
        """Main polling loop."""
        while self.is_running:
            try:
                for directory in self.watch_directories:
                    if not directory.exists():
                        continue
                    
                    for filepath in directory.rglob('*'):
                        if not filepath.is_file():
                            continue
                        
                        filepath_str = str(filepath)
                        if filepath_str in self.known_files:
                            continue
                        
                        if self._should_process(filepath):
                            # Wait for file to be stable
                            if wait_for_file_ready(filepath_str, timeout=10):
                                self.known_files.add(filepath_str)
                                try:
                                    logger.info(f"Processing new file: {filepath_str}")
                                    self.callback(filepath_str)
                                except Exception as e:
                                    logger.error(f"Error processing file {filepath_str}: {e}")
            
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
            
            time.sleep(self.poll_interval)
    
    def _should_process(self, filepath: Path) -> bool:
        """Check if file should be processed."""
        return filepath.suffix.lower() in self.file_extensions

