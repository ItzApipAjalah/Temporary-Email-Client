from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import string
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
import json
import os

class LoadingLabel(ttk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]
        self.current_frame = 0
        self.is_animating = False
        self.configure(font=("Consolas", 24)) 

    def start_animation(self):
        self.is_animating = True
        self._animate()

    def stop_animation(self):
        self.is_animating = False
        self.configure(text="") 

    def _animate(self):
        if self.is_animating:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.configure(text=self.frames[self.current_frame])
            self.after(100, self._animate)  # Update every 100ms

class TempMailScraper:
    def __init__(self, domain="mailto.plus", username=None, pin=None):
        self.base_url = "https://tempmail.plus/en/#!"
        self.domain = domain
        self.username = username
        self.pin = pin
        self.random_username = None
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--log-level=3')  # Reduce logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        # Setup service and driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.current_email = None
        
        # Create screenshots directory if it doesn't exist
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def generate_random_username(self, length=10):
        """Generate a random username for the email"""
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    def create_email(self):
        """Create a new temporary email"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            input_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "pre_button"))
            )
            input_field.send_keys(Keys.CONTROL + "a")
            input_field.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Take screenshot after entering username
            screenshot_path = os.path.join(
                self.screenshot_dir, 
                f"screenshot_username_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            
            if self.domain != "mailto.plus":
                if not self.username or not self.pin:
                    raise Exception("Username and PIN required for custom domain")
                    
                # Enter username
                for char in self.username:
                    input_field.send_keys(char)
                    time.sleep(0.1)
                
                input_field.send_keys(Keys.RETURN)
                time.sleep(3)
                
                # Handle PIN
                pin_input = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "pin"))
                )
                pin_input.send_keys(Keys.CONTROL + "a")
                pin_input.send_keys(Keys.DELETE)
                time.sleep(0.5)
                
                for char in self.pin:
                    pin_input.send_keys(char)
                    time.sleep(0.1)
                
                time.sleep(1)
                
                # Take screenshot after entering PIN
                screenshot_path = os.path.join(
                    self.screenshot_dir, 
                    f"screenshot_pin_{int(time.time())}.png"
                )
                self.driver.save_screenshot(screenshot_path)
                
                verify_button = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "verify"))
                )
                verify_button.click()
            else:
                random_name = self.random_username
                for char in random_name:
                    input_field.send_keys(char)
                    time.sleep(0.1)
                input_field.send_keys(Keys.RETURN)
            
            # Wait for email to be generated
            time.sleep(3)
            
            # Get the email from the input field
            input_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "pre_button"))
            )
            username = input_field.get_attribute("value")
            
            # Use custom domain if set
            if self.domain != "mailto.plus":
                self.current_email = f"{username}@{self.domain}"
            else:
                self.current_email = f"{username}@mailto.plus"
            
            # Take screenshot of generated email
            screenshot_path = os.path.join(
                self.screenshot_dir, 
                f"screenshot_generated_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            
            return self.current_email
            
        except Exception as e:
            # Save error screenshot in screenshots directory
            screenshot_path = os.path.join(
                self.screenshot_dir, 
                f"screenshot_error_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            raise Exception(f"Failed to create email. Screenshot saved as {screenshot_path}")
    
    def check_new_messages(self):
        """Check for new messages"""
        try:
            # Wait for inbox messages
            messages = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "mail"))
            )
            
            new_messages = []
            for message in messages:
                try:
                    # Extract message details
                    from_element = message.find_element(By.CLASS_NAME, "from")
                    sender = from_element.find_element(By.CLASS_NAME, "font-weight-bold").text
                    subject = message.find_element(By.CLASS_NAME, "subj").text
                    
                    onclick = message.get_attribute("onclick")
                    message_id = onclick.split("'")[1].split("/")[1]
                    
                    new_messages.append({
                        'id': message_id,
                        'from': sender,
                        'subject': subject
                    })
                except Exception as e:
                    print(f"Error parsing message: {str(e)}")
                    continue
            
            return new_messages
            
        except TimeoutException:
            return [] 
        except Exception as e:
            raise Exception(f"Failed to check messages: {str(e)}")
    
    def get_message_content(self, message_id):
        """Get content of a specific message"""
        try:
            # Navigate to message
            self.driver.get(f"{self.base_url}mail/{message_id}")
            
            # Wait for page load after redirect
            time.sleep(2)
            
            # Wait for message content to load with longer timeout
            info_div = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "info"))
            )
            
            # Additional wait to ensure content is loaded
            time.sleep(1)
            
            # Extract message details
            # Get the email address from the text-muted span
            sender = info_div.find_element(By.CLASS_NAME, "text-muted").text.strip('<>')
            
            # Get date
            date = info_div.find_element(By.CLASS_NAME, "date").get_attribute("data-date")
            
            # Get subject from div with class "subject mb-20"
            subject = info_div.find_element(By.CSS_SELECTOR, "div.subject.mb-20").text
            
            # Get content from div with dir="ltr"
            content = info_div.find_element(By.CSS_SELECTOR, "div[dir='ltr']").text
            
            # Take screenshot of message content
            screenshot_path = os.path.join(
                self.screenshot_dir, 
                f"screenshot_message_{message_id}_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            
            return {
                'from': sender,
                'date': date,
                'subject': subject,
                'text': content,
                'screenshot': screenshot_path  
            }
            
        except Exception as e:
            # Save error screenshot
            screenshot_path = os.path.join(
                self.screenshot_dir, 
                f"screenshot_message_error_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            raise Exception(f"Failed to get message content. Screenshot saved as {screenshot_path}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

class TempMailGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Temporary Email Client")
        self.root.geometry("1000x700")
        
        # Set theme
        self.style = ttk.Style(theme="darkly")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with warning
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_left = ttk.Frame(header_frame)
        header_left.pack(side=tk.LEFT)
        
        ttk.Label(
            header_left, 
            text="Temporary Email Client",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-primary"
        ).pack(anchor="w")
        
        ttk.Label(
            header_left,
            text="⚠️ Email is temporary and will be deleted after receiving a message",
            font=("Helvetica", 10),
            bootstyle="warning"
        ).pack(anchor="w", pady=(2, 0))
        
        self.email_frame = ttk.LabelFrame(
            self.main_frame,
            text="Email Address",
            padding="10",
            bootstyle="primary"
        )
        self.email_frame.pack(fill=tk.X, pady=(0, 20))
        
        email_content_frame = ttk.Frame(self.email_frame)
        email_content_frame.pack(fill=tk.X)
        
        domain_frame = ttk.Frame(self.email_frame)
        domain_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            domain_frame,
            text="Domain:",
            font=("Helvetica", 11)
        ).pack(side=tk.LEFT)
        
        self.domain_var = tk.StringVar(value="")  # Empty default value
        self.domain_entry = ttk.Entry(
            domain_frame,
            textvariable=self.domain_var,
            width=30
        )
        self.domain_entry.pack(side=tk.LEFT, padx=10)
        
        self.config_file = "tempmail.json"
        self.saved_credentials = self.load_credentials()
        
        if self.saved_credentials:
            first_domain = next(iter(self.saved_credentials))
            self.domain_var.set(first_domain)
            self.domain_entry.configure(foreground="white")
        else:
            self.domain_entry.insert(0, "Custom domain (optional)")
            self.domain_entry.configure(foreground="gray")
            self.domain_entry.bind("<FocusIn>", self.on_domain_entry_focus_in)
            self.domain_entry.bind("<FocusOut>", self.on_domain_entry_focus_out)
        
        # Add custom domain credentials frame
        self.credentials_frame = ttk.Frame(self.email_frame)
        
        # Username input
        username_frame = ttk.Frame(self.credentials_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            username_frame,
            text="Username:",
            font=("Helvetica", 11)
        ).pack(side=tk.LEFT)
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var,
            width=20
        )
        self.username_entry.pack(side=tk.LEFT, padx=10)
        
        # PIN input
        pin_frame = ttk.Frame(self.credentials_frame)
        pin_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            pin_frame,
            text="PIN:",
            font=("Helvetica", 11)
        ).pack(side=tk.LEFT)
        
        self.pin_var = tk.StringVar()
        self.pin_entry = ttk.Entry(
            pin_frame,
            textvariable=self.pin_var,
            width=20,
            show="*"  # Hide PIN
        )
        self.pin_entry.pack(side=tk.LEFT, padx=10)
        
        # Initialize credentials if we have them
        if self.saved_credentials:
            first_domain = next(iter(self.saved_credentials))
            creds = self.saved_credentials[first_domain]
            self.username_var.set(creds["username"])
            self.pin_var.set(creds["pin"])
            self.credentials_frame.pack(fill=tk.X, pady=5)
        
        # Add domain change handler
        self.domain_var.trace_add("write", self.on_domain_change)
        
        self.email_label = ttk.Label(
            email_content_frame,
            text="Your temporary email:",
            font=("Helvetica", 12)
        )
        self.email_label.pack(side=tk.LEFT)
        
        self.email_value = ttk.Label(
            email_content_frame,
            text="Not generated yet",
            font=("Helvetica", 12, "bold"),
            bootstyle="primary"
        )
        self.email_value.pack(side=tk.LEFT, padx=10)
        
        self.copy_button = ttk.Button(
            email_content_frame,
            text="Copy",
            command=self.copy_email,
            bootstyle="info-outline",
            width=8,
            state="disabled"  
        )
        self.copy_button.pack(side=tk.LEFT)
        
        # Loading animation
        self.loading_label = LoadingLabel(
            email_content_frame,
            bootstyle="primary",  
        )
        self.loading_label.pack(side=tk.LEFT, padx=10)
        
        self.generate_button = ttk.Button(
            email_content_frame,
            text="Generate New Email",
            command=self.start_email_generation,
            bootstyle="success-outline"
        )
        self.generate_button.pack(side=tk.RIGHT)
        
        # Messages frame
        self.messages_frame = ttk.LabelFrame(
            self.main_frame,
            text="Messages",
            padding="10",
            bootstyle="primary"
        )
        self.messages_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget for messages
        self.messages_text = ttk.Text(
            self.messages_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 11)
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(
            self.messages_frame,
            orient="vertical",
            command=self.messages_text.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_text.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            bootstyle="primary",
            padding=5
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.mail_scraper = None
        self.monitoring = False
        self.monitor_thread = None
        
        self.is_closing = False
        
        self.style.configure('danger.TButton', font=('Helvetica', 10))
        self.style.configure('secondary.TButton', font=('Helvetica', 10))
        
        self.current_email = None
        self.display_email = None  

    def generate_random_username(self, length=10):
        """Generate a random username for display"""
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    def start_email_generation(self):
        self.generate_button.configure(state="disabled")
        self.status_var.set("Generating email address...")
        self.loading_label.start_animation()
        
        def generate():
            try:
                # Get domain and check if it's the placeholder text
                current_domain = self.domain_var.get().strip()
                if current_domain == "Custom domain (optional)":
                    current_domain = ""
                
                if current_domain:
                    username = self.username_var.get().strip()
                    pin = self.pin_var.get().strip()
                    if username and pin:
                        self.save_credentials(current_domain, username, pin)
                
                random_username = self.generate_random_username()
                
                # Create new scraper if domain changed
                if (not self.mail_scraper or 
                    self.mail_scraper.domain != current_domain):
                    if self.mail_scraper:
                        self.mail_scraper.close()
                    self.mail_scraper = TempMailScraper(
                        domain=current_domain if current_domain else "mailto.plus",
                        username=self.username_var.get().strip() if current_domain else None,
                        pin=self.pin_var.get().strip() if current_domain else None
                    )
                
                if not current_domain:
                    self.mail_scraper.random_username = random_username
                
                email = self.mail_scraper.create_email()
                
                self.root.after(0, self.update_email_address, email, random_username)
                self.root.after(0, self.start_monitoring)
                
            except Exception as e:
                self.root.after(0, self.show_error, f"Error generating email: {str(e)}")
                self.root.after(0, lambda: self.generate_button.configure(state="normal"))
            finally:
                self.root.after(0, self.loading_label.stop_animation)
        
        threading.Thread(target=generate, daemon=True).start()

    def copy_email(self):
        """Copy display email address to clipboard"""
        if self.display_email: 
            self.root.clipboard_clear()
            self.root.clipboard_append(self.display_email)
            
            # Show feedback in status bar
            prev_status = self.status_var.get()
            self.status_var.set("Email copied to clipboard!")
            
            # Reset status after 2 seconds
            self.root.after(2000, lambda: self.status_var.set(prev_status))

    def update_email_address(self, email, random_username):
        self.current_email = email 
        
        domain = self.domain_var.get().strip()
        
        if domain == "Custom domain (optional)" or not domain:
            self.display_email = f"{random_username}@mailto.plus"
        else:
            self.display_email = f"{random_username}@{domain}"
        
        self.email_value.configure(text=self.display_email)
        self.status_var.set("Email address generated successfully")
        self.generate_button.configure(state="normal")
        self.copy_button.configure(state="normal")

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_messages, daemon=True)
            self.monitor_thread.start()

    def monitor_messages(self):
        while self.monitoring:
            try:
                messages = self.mail_scraper.check_new_messages()
                
                if messages:
                    for msg in messages:
                        content = self.mail_scraper.get_message_content(msg['id'])
                        self.root.after(0, self.display_message, content)
                
                time.sleep(10)
                
            except Exception as e:
                self.root.after(0, self.show_error, f"Error checking messages: {str(e)}")
                time.sleep(10)

    def display_message(self, content):
        message_text = f"\n{'='*50}\n"
        message_text += f"From: {content['from']}\n"
        message_text += f"Date: {content['date']}\n"
        message_text += f"Subject: {content['subject']}\n"
        message_text += f"Content: {content['text']}\n"
        if 'screenshot' in content:
            message_text += f"Screenshot saved: {content['screenshot']}\n"
        message_text += f"{'='*50}\n"
        
        self.messages_text.insert(tk.END, message_text)
        self.messages_text.see(tk.END)
        self.status_var.set("New message received")

    def show_error(self, error_message):
        self.status_var.set(f"Error: {error_message}")

    def show_confirmation_dialog(self):
        """Show a confirmation dialog before closing"""
        dialog = ttk.Toplevel(self.root)
        dialog.title("Confirm Exit")
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry("300x150")
        dialog_x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
        dialog_y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        
        ttk.Label(
            dialog,
            text="Are you sure you want to exit?\nThis will close all browser windows.",
            justify="center",
            font=("Helvetica", 11),
            wraplength=250
        ).pack(pady=20)
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def confirm():
            dialog.destroy()
            self.perform_closing()
            
        def cancel():
            dialog.destroy()
        
        ttk.Button(
            button_frame,
            text="Exit",
            command=confirm,
            bootstyle="danger",
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=cancel,
            bootstyle="secondary",
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", cancel)
        
        # Make dialog non-resizable
        dialog.resizable(False, False)

    def perform_closing(self):
        """Perform actual closing operations"""
        if self.is_closing:
            return
            
        self.is_closing = True
        self.status_var.set("Closing application...")
        
        # Disable all buttons
        self.generate_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        
        # Stop monitoring
        self.monitoring = False
        
        def cleanup():
            try:
                # Close browser
                if self.mail_scraper:
                    self.mail_scraper.close()
                
                # Destroy root window
                self.root.after(0, self.root.destroy)
                
            except Exception as e:
                print(f"Error during cleanup: {e}")
                self.root.destroy()
        
        # Run cleanup in thread
        threading.Thread(target=cleanup, daemon=True).start()

    def on_closing(self):
        """Handle window close button click"""
        if not self.is_closing:
            self.show_confirmation_dialog()

    def on_domain_entry_focus_in(self, event):
        """Handle domain entry focus in"""
        if self.domain_entry.get() == "Custom domain (optional)":
            self.domain_entry.delete(0, tk.END)
            self.domain_entry.configure(foreground="white") 

    def on_domain_entry_focus_out(self, event):
        """Handle domain entry focus out"""
        if not self.domain_entry.get():
            self.domain_entry.insert(0, "Custom domain (optional)")
            self.domain_entry.configure(foreground="gray")

    def on_domain_change(self, *args):
        """Handle domain input changes"""
        domain = self.domain_var.get().strip()
        if domain and domain != "Custom domain (optional)":
            self.credentials_frame.pack(fill=tk.X, pady=5)
            
            if domain in self.saved_credentials:
                creds = self.saved_credentials[domain]
                self.username_var.set(creds["username"])
                self.pin_var.set(creds["pin"])
        else:
            self.credentials_frame.pack_forget()

    def load_credentials(self):
        """Load saved credentials from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_credentials(self, domain, username, pin):
        """Save credentials to JSON file"""
        credentials = self.load_credentials()
        credentials[domain] = {
            "username": username,
            "pin": pin
        }
        with open(self.config_file, 'w') as f:
            json.dump(credentials, f, indent=4)
        self.saved_credentials = credentials

def main():
    def handle_signal(signum, frame):
        if app and not app.is_closing:
            app.perform_closing()
    
    # Register signal handlers
    import signal
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    root = ttk.Window(themename="darkly")
    app = TempMailGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        if not app.is_closing:
            app.perform_closing()

if __name__ == "__main__":
    main() 