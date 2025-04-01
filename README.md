TempMail Generator - Build & Usage Instructions
=============================================

Requirements:
------------
1. Python 3.8 or higher
2. Chrome browser installed

Build Instructions:
-----------------
1. Install Python requirements:
   - Open PowerShell/Command Prompt
   - Run: pip install -r requirements.txt

2. Build the executable:
   - Right-click build.ps1
   - Select "Run with PowerShell"
   - Wait for build to complete
   - The executable will be in the 'dist' folder

Manual Build (if build.ps1 fails):
--------------------------------
1. Install PyInstaller:
   pip install pyinstaller

2. Run PyInstaller command:
   python -m PyInstaller --noconfirm --onefile --windowed --name "TempMail" --hidden-import "ttkbootstrap" --hidden-import "webdriver_manager" --hidden-import "selenium" mail_generator.py

Running the Application:
----------------------
Method 1 (From Source):
- Run: python mail_generator.py

Method 2 (Executable):
- Go to 'dist' folder
- Run TempMail.exe

Features:
--------
- Generate temporary email addresses
- Support for custom domains
- Auto-save domain credentials

Notes:
-----
- First run may take longer due to Chrome driver download
- Screenshots are saved in 'screenshots' folder
- Custom domain credentials are saved in 'tempmail.json'
- Email is temporary and will be deleted after receiving a message

Troubleshooting:
--------------
1. If exe fails to start:
   - Try running from source first
   - Check Chrome is installed
   - Check antivirus isn't blocking

2. If build fails:
   - Try manual build instructions
   - Make sure all requirements are installed
   - Run as administrator if needed

For custom domains:
-----------------
1. Enter your domain
2. Enter username and PIN can find in the [tempmail](https://tempmail.plus/)
3. Credentials will be saved automatically
4. Next time, credentials will auto-fill 