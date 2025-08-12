import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json

class LogCollector:
    def __init__(self, source_type, event_queue):
        self.source_type = source_type
        self.event_queue = event_queue
        self.logger = logging.getLogger(__name__)
        self.setup_source_config()
        
    def setup_source_config(self):
        """Configure source-specific settings"""
        # Use local log files for testing
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        self.source_configs = {
            'system': {
                'paths': [os.path.join(log_dir, 'system.log')],
                'patterns': ['error', 'warning', 'critical', 'failed']
            },
            'network': {
                'paths': [os.path.join(log_dir, 'network.log')],
                'patterns': ['403', '404', '500', 'denied']
            },
            'application': {
                'paths': [os.path.join(log_dir, 'app.log')],
                'patterns': ['exception', 'error', 'crash', 'failed']
            }
        }
        
        self.config = self.source_configs.get(self.source_type, {
            'paths': [],
            'patterns': []
        })
        
        # Create empty log files if they don't exist
        for path in self.config['paths']:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(f"# {self.source_type} log file created at {datetime.now().isoformat()}\n")
                self.logger.info(f"Created log file: {path}")
        
    class LogEventHandler(FileSystemEventHandler):
        def __init__(self, collector):
            self.collector = collector
            
        def on_modified(self, event):
            if not event.is_directory and event.src_path in self.collector.config['paths']:
                self.collector.process_log_file(event.src_path)
                
    def process_log_file(self, file_path):
        """Process new log entries from the file"""
        try:
            with open(file_path, 'r') as f:
                # Seek to end minus 4KB to read recent entries
                f.seek(max(0, os.path.getsize(file_path) - 4096))
                recent_logs = f.readlines()
                
                for line in recent_logs:
                    if any(pattern in line.lower() for pattern in self.config['patterns']):
                        event = {
                            'timestamp': datetime.now().isoformat(),
                            'source': self.source_type,
                            'file': file_path,
                            'content': line.strip(),
                            'severity': self.determine_severity(line)
                        }
                        self.event_queue.put(event)
                        
        except Exception as e:
            self.logger.error(f"Error processing log file {file_path}: {str(e)}")
            
    def determine_severity(self, log_line):
        """Determine the severity of the log entry"""
        log_lower = log_line.lower()
        if any(critical in log_lower for critical in ['critical', 'emergency', 'alert']):
            return 'CRITICAL'
        elif any(error in log_lower for error in ['error', 'failure', 'failed']):
            return 'ERROR'
        elif any(warning in log_lower for warning in ['warning', 'warn']):
            return 'WARNING'
        return 'INFO'
        
    def run(self):
        """Start the log collector"""
        self.logger.info(f"Starting {self.source_type} log collector")
        
        # Create a single observer for all files
        observer = Observer()
        event_handler = self.LogEventHandler(self)
        
        # Get unique directories to watch
        log_dirs = {os.path.dirname(path) for path in self.config['paths']}
        
        # Schedule watching each directory
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            observer.schedule(event_handler, log_dir, recursive=False)
            
        observer.start()
        self.logger.info(f"Monitoring files: {', '.join(self.config['paths'])}")
                
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join() 