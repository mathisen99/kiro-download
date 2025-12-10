# Kiro Downloader

A Python script to automatically download, install, and manage [Kiro IDE](https://kiro.dev) on Linux x64 systems.

## Features

✨ **Smart Version Management** - Automatically checks for updates and prevents re-downloading the same version  
🎨 **Beautiful Terminal Output** - Colored output with progress bars for better UX  
📦 **Automatic Extraction** - Downloads and extracts Kiro to the script directory  
�️ **Desktop Integration** - Creates launcher wrapper and desktop entry for GUI launchers (Hyprland, GNOME, KDE, etc.)  
�🔗 **System-wide Access** - Creates a symbolic link to `/usr/local/bin/kiro` for easy terminal access  
⚡ **Quick Update Check** - Use `--check` flag to see if updates are available without downloading  
🚀 **Background Execution** - Launcher wrapper runs Kiro detached from terminal  

## Requirements

- Python 3.6+
- Linux x64 system
- `sudo` access (for creating symbolic link)
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/kiro-downloader.git
cd kiro-downloader
```

2. Make the script executable:
```bash
chmod +x download_kiro.py
```

3. Run the script:
```bash
python3 download_kiro.py
```

## Usage

### Download and Install Latest Version
```bash
python3 download_kiro.py
```

This will:
- Fetch the latest version metadata
- Download the Kiro tar.gz file
- Extract it to the script directory
- Create a launcher wrapper script (`kiro-launcher.sh`) that runs Kiro detached from terminal
- Create a desktop entry for your application launcher (Hyprland, GNOME, KDE, etc.)
- Create a symbolic link at `/usr/local/bin/kiro` for terminal access
- Clean up the downloaded tarball

### Check for Updates
```bash
python3 download_kiro.py --check
```

This will check if a new version is available without downloading anything.

### Run Kiro

After installation, you can run Kiro in multiple ways:

**From Terminal:**
```bash
kiro  # Runs in foreground, attached to terminal
```

**From Application Launcher:**
- Search for "Kiro" in your application launcher (Hyprland, Rofi, GNOME, KDE, etc.)
- Click to launch - runs detached from terminal in the background

**Using the Launcher Wrapper:**
```bash
./kiro-launcher.sh  # Runs in background, detached from terminal
```

The launcher wrapper is automatically created during installation and prevents terminal spam while allowing you to close the terminal without killing Kiro.

## Optional: Create an Alias

Add this line to your `~/.zshrc` or `~/.bashrc`:

```bash
alias kiro-update='python3 /path/to/download_kiro.py'
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Now you can use:
```bash
kiro-update          # Install/update Kiro
kiro-update --check  # Check for updates
```

## How It Works

1. **Fetches Metadata**: Downloads version information from Kiro's update server
2. **Version Comparison**: Compares installed version (stored in `.kiro_version`) with the latest available
3. **Smart Download**: Only downloads if a new version is available
4. **Auto-extraction**: Extracts the tarball to `./Kiro/` directory
5. **Binary Location**: Finds the Kiro binary in the extracted files
6. **Desktop Integration**: Creates launcher wrapper and desktop entry for GUI launchers
7. **Symlink Creation**: Creates `/usr/local/bin/kiro` → `./Kiro/kiro` (requires sudo)
8. **Cleanup**: Removes the downloaded tarball to save space

## File Structure

```
kiro-downloader/
├── download_kiro.py    # Main script
├── kiro-launcher.sh    # Launcher wrapper (auto-generated)
├── kiro.desktop        # Desktop entry (auto-generated)
├── .kiro_version       # Tracks installed version (auto-generated)
├── Kiro/              # Extracted Kiro installation (auto-generated)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Example Output

```
============================================================
🚀 Kiro Downloader - Linux x64 Stable
============================================================
🌐 Fetching metadata...

📦 Latest version: 0.7.34
💻 Installed version: 0.7.33

────────────────────────────────────────────────────────────
📥 Downloading from: https://prod.download.desktop.kiro.dev/...
💾 Saving to: /path/to/kiro-ide-0.7.34-stable-linux-x64.tar.gz
Progress: [████████████████████████████████████████] 100% (244.33 MB / 244.33 MB)
✓ Download complete!

────────────────────────────────────────────────────────────

📦 Extracting kiro-ide-0.7.34-stable-linux-x64.tar.gz...
✓ Extraction complete!

🔍 Locating Kiro binary...
✓ Found binary: /path/to/Kiro/kiro

🖥️  Setting up desktop integration...
✓ Created launcher wrapper: /path/to/kiro-launcher.sh
✓ Created desktop entry: /home/user/.local/share/applications/kiro.desktop
  Kiro should now appear in your application launcher!

🔗 Creating symbolic link...
✓ Symbolic link created: /usr/local/bin/kiro -> /path/to/Kiro/kiro
  You can now run 'kiro' from anywhere!

🧹 Cleaning up tarball...
✓ Tarball removed

============================================================
✓ Successfully installed Kiro v0.7.34
  Location: /path/to/kiro-downloader
  Binary: /path/to/Kiro/kiro
  Total size: ~707.64 MB
============================================================
```

## Troubleshooting

### Sudo Password Required
During installation, the script creates a system-wide symlink at `/usr/local/bin/kiro` which requires `sudo` access.

**If you have sudo password enabled:**
- You'll be prompted to enter your password during installation
- Enter your password and the installation will continue normally

**If you don't have sudo access or prefer not to use it:**
You can still use Kiro without the system-wide symlink:

1. **Use the launcher wrapper directly:**
   ```bash
   /path/to/kiro-downloader/kiro-launcher.sh
   ```

2. **Create a shell alias** (add to `~/.zshrc` or `~/.bashrc`):
   ```bash
   alias kiro='/path/to/kiro-downloader/kiro-launcher.sh'
   ```

3. **Use the application launcher:**
   - The desktop entry works without sudo
   - Search for "Kiro" in your application launcher

### Permission Denied for Symlink Creation
If you get a permission error when creating the symlink, the script will provide instructions to manually create it:
```bash
sudo ln -s /path/to/kiro-launcher.sh /usr/local/bin/kiro
```

### Binary Not Found
If the script can't locate the Kiro binary after extraction, check the `Kiro/` directory manually and verify the extraction was successful.

### Network Issues
If download fails, check your internet connection and try again. The script will show detailed error messages.

### Kiro Not Appearing in Launcher
If Kiro doesn't appear in your application launcher after installation:
1. Try logging out and back in
2. Manually run: `update-desktop-database ~/.local/share/applications/`
3. Check if the desktop file exists: `ls ~/.local/share/applications/kiro.desktop`

### Terminal Spam When Running Kiro
Use the launcher wrapper or application launcher instead of running `kiro` directly:
```bash
./kiro-launcher.sh  # Runs detached from terminal
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This is an unofficial downloader script. Kiro IDE and all related trademarks belong to their respective owners.

## Links

- [Kiro IDE Official Website](https://kiro.dev)
- [Report Issues](https://github.com/yourusername/kiro-downloader/issues)
