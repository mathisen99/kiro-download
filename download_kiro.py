#!/usr/bin/env python3
"""
Kiro Downloader - Downloads the latest stable version of Kiro for Linux x64
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path


# Configuration
METADATA_URL = "https://prod.download.desktop.kiro.dev/stable/metadata-linux-x64-stable.json"
SCRIPT_DIR = Path(__file__).parent.resolve()
VERSION_FILE = SCRIPT_DIR / ".kiro_version"
SYMLINK_PATH = Path("/usr/local/bin/kiro")

# ANSI Color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def cprint(text, color="", bold=False, end="\n"):
    """Print colored text to terminal."""
    style = Colors.BOLD if bold else ""
    print(f"{style}{color}{text}{Colors.RESET}", end=end)


def fetch_metadata():
    """Fetch the metadata JSON from the Kiro server."""
    cprint("🌐 Fetching metadata...", Colors.CYAN)
    try:
        with urllib.request.urlopen(METADATA_URL) as response:
            data = response.read()
            return json.loads(data)
    except Exception as e:
        cprint(f"✗ Error fetching metadata: {e}", Colors.RED, bold=True)
        sys.exit(1)


def find_tarball_url(metadata):
    """Extract the tar.gz download URL from metadata."""
    current_version = metadata.get("currentRelease")
    if not current_version:
        cprint("✗ Error: No current release found in metadata", Colors.RED, bold=True)
        sys.exit(1)
    
    # Find the tar.gz file in releases
    for release in metadata.get("releases", []):
        update_to = release.get("updateTo", {})
        url = update_to.get("url", "")
        if url.endswith(".tar.gz"):
            return current_version, url
    
    cprint("✗ Error: No tar.gz file found in releases", Colors.RED, bold=True)
    sys.exit(1)


def get_installed_version():
    """Get the currently installed version from version file."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return None


def save_installed_version(version):
    """Save the installed version to version file."""
    VERSION_FILE.write_text(version)


def download_file(url, destination):
    """Download a file with progress indication."""
    cprint(f"📥 Downloading from: {url}", Colors.BLUE)
    cprint(f"💾 Saving to: {destination}", Colors.BLUE)
    
    try:
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\r{Colors.CYAN}Progress: [{bar}] {percent}% ({downloaded_mb:.2f} MB / {total_mb:.2f} MB){Colors.RESET}", end="")
        
        urllib.request.urlretrieve(url, destination, reporthook=report_progress)
        print()  # New line after progress
        cprint("✓ Download complete!", Colors.GREEN, bold=True)
        return True
    except Exception as e:
        cprint(f"\n✗ Error downloading file: {e}", Colors.RED, bold=True)
        return False


def extract_tarball(tarball_path, extract_to):
    """Extract tar.gz file to specified directory."""
    cprint(f"\n📦 Extracting {tarball_path.name}...", Colors.CYAN)
    try:
        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
        cprint("✓ Extraction complete!", Colors.GREEN, bold=True)
        return True
    except Exception as e:
        cprint(f"✗ Error extracting file: {e}", Colors.RED, bold=True)
        return False


def find_kiro_binary(extract_dir):
    """Find the Kiro binary in the extracted directory."""
    # Common locations for the binary
    possible_paths = [
        extract_dir / "kiro",
        extract_dir / "bin" / "kiro",
        extract_dir / "Kiro" / "kiro",
    ]
    
    # Search recursively if not found in common locations
    for path in possible_paths:
        if path.exists() and path.is_file():
            return path
    
    # Fallback: search for any file named 'kiro'
    for path in extract_dir.rglob("kiro"):
        if path.is_file() and os.access(path, os.X_OK):
            return path
    
    return None


def create_launcher_wrapper():
    """Create a launcher wrapper script that runs Kiro detached from terminal."""
    launcher_path = SCRIPT_DIR / "kiro-launcher.sh"
    launcher_content = f"""#!/bin/bash
# Kiro launcher wrapper - runs Kiro detached from terminal

# Resolve the real path of this script (follows symlinks)
SCRIPT_PATH="$(readlink -f "${{BASH_SOURCE[0]}}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
KIRO_BINARY="$SCRIPT_DIR/Kiro/kiro"

# Check if Kiro binary exists
if [ ! -f "$KIRO_BINARY" ]; then
    echo "Error: Kiro binary not found at $KIRO_BINARY"
    echo "Please run download_kiro.py first to install Kiro"
    exit 1
fi

# If this is just a shell integration query, pass it through directly (no nohup)
if [[ "$*" == *"--locate-shell-integration-path"* ]]; then
    exec "$KIRO_BINARY" "$@"
    exit 0
fi

# Launch Kiro in the background, detached from terminal
# Redirect output to /dev/null to prevent terminal spam
nohup "$KIRO_BINARY" "$@" > /dev/null 2>&1 &

# Disown the process so it survives terminal closure
disown

exit 0
"""
    
    try:
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        cprint(f"✓ Created launcher wrapper: {launcher_path}", Colors.GREEN)
        return launcher_path
    except Exception as e:
        cprint(f"⚠ Warning: Could not create launcher wrapper: {e}", Colors.YELLOW)
        return None


def create_desktop_entry(launcher_path):
    """Create desktop entry for application launchers."""
    desktop_file = SCRIPT_DIR / "kiro.desktop"
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Kiro
Comment=Kiro IDE - AI-powered code editor
Exec={launcher_path}
Icon={SCRIPT_DIR}/Kiro/resources/app/extensions/theme-seti/icons/seti-circular-128x128.png
Terminal=false
Categories=Development;IDE;TextEditor;
StartupNotify=true
StartupWMClass=Kiro
"""
    
    try:
        # Write desktop file
        desktop_file.write_text(desktop_content)
        
        # Install to user applications directory
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        dest_desktop = apps_dir / "kiro.desktop"
        dest_desktop.write_text(desktop_content)
        
        # Update desktop database
        try:
            subprocess.run(["update-desktop-database", str(apps_dir)], 
                         check=False, capture_output=True)
        except:
            pass  # Not critical if this fails
        
        cprint(f"✓ Created desktop entry: {dest_desktop}", Colors.GREEN)
        cprint(f"  Kiro should now appear in your application launcher!", Colors.GREEN)
        return True
    except Exception as e:
        cprint(f"⚠ Warning: Could not create desktop entry: {e}", Colors.YELLOW)
        return False


def create_symlink(launcher_path):
    """Create symbolic link to /usr/local/bin/kiro pointing to launcher wrapper."""
    cprint(f"\n🔗 Creating symbolic link...", Colors.CYAN)
    try:
        # Remove existing symlink if it exists
        if SYMLINK_PATH.exists() or SYMLINK_PATH.is_symlink():
            cprint(f"  Removing existing symlink: {SYMLINK_PATH}", Colors.YELLOW)
            subprocess.run(["sudo", "rm", "-f", str(SYMLINK_PATH)], check=True)
        
        # Create new symlink to launcher wrapper (not binary)
        subprocess.run(["sudo", "ln", "-s", str(launcher_path), str(SYMLINK_PATH)], check=True)
        cprint(f"✓ Symbolic link created: {SYMLINK_PATH} -> {launcher_path}", Colors.GREEN, bold=True)
        cprint(f"  You can now run 'kiro' from anywhere (detached from terminal)!", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        cprint(f"✗ Error creating symbolic link: {e}", Colors.RED, bold=True)
        cprint(f"  You may need to run this script with sudo or manually create the link:", Colors.YELLOW)
        cprint(f"  sudo ln -s {launcher_path} {SYMLINK_PATH}", Colors.YELLOW)
        return False


def check_for_updates():
    """Check if there's a new version available."""
    metadata = fetch_metadata()
    latest_version, _ = find_tarball_url(metadata)
    installed_version = get_installed_version()
    
    cprint("\n" + "=" * 60, Colors.MAGENTA)
    cprint("📊 Version Check", Colors.MAGENTA, bold=True)
    cprint("=" * 60, Colors.MAGENTA)
    
    cprint(f"\n📦 Latest version:    {latest_version}", Colors.CYAN, bold=True)
    if installed_version:
        cprint(f"💻 Installed version: {installed_version}", Colors.BLUE, bold=True)
    else:
        cprint(f"💻 Installed version: Not installed", Colors.YELLOW, bold=True)
    
    if installed_version == latest_version:
        cprint("\n✓ You have the latest version!", Colors.GREEN, bold=True)
        return False
    elif installed_version:
        cprint(f"\n⚠ Update available: {installed_version} → {latest_version}", Colors.YELLOW, bold=True)
        return True
    else:
        cprint("\n📥 Kiro is not installed yet", Colors.YELLOW, bold=True)
        return True


def main():
    """Main function to orchestrate the download process."""
    parser = argparse.ArgumentParser(description="Kiro Downloader - Linux x64 Stable")
    parser.add_argument("--check", action="store_true", help="Check for updates without downloading")
    args = parser.parse_args()
    
    # Header
    cprint("\n" + "=" * 60, Colors.MAGENTA, bold=True)
    cprint("🚀 Kiro Downloader - Linux x64 Stable", Colors.MAGENTA, bold=True)
    cprint("=" * 60, Colors.MAGENTA, bold=True)
    
    # Check-only mode
    if args.check:
        check_for_updates()
        return
    
    # Fetch and parse metadata
    metadata = fetch_metadata()
    latest_version, download_url = find_tarball_url(metadata)
    installed_version = get_installed_version()
    
    cprint(f"\n📦 Latest version: {latest_version}", Colors.CYAN, bold=True)
    if installed_version:
        cprint(f"💻 Installed version: {installed_version}", Colors.BLUE)
    
    # Check if already up to date
    if installed_version == latest_version:
        cprint(f"\n✓ You already have the latest version ({latest_version})!", Colors.GREEN, bold=True)
        cprint("  Use --check to check for updates", Colors.CYAN)
        return
    
    # Determine filename and destination
    filename = f"kiro-ide-{latest_version}-stable-linux-x64.tar.gz"
    tarball_path = SCRIPT_DIR / filename
    
    # Download the file
    cprint(f"\n{'─' * 60}", Colors.BLUE)
    success = download_file(download_url, tarball_path)
    
    if not success:
        sys.exit(1)
    
    # Extract the tarball
    cprint(f"\n{'─' * 60}", Colors.BLUE)
    if not extract_tarball(tarball_path, SCRIPT_DIR):
        sys.exit(1)
    
    # Find the Kiro binary
    cprint(f"\n🔍 Locating Kiro binary...", Colors.CYAN)
    binary_path = find_kiro_binary(SCRIPT_DIR)
    
    if not binary_path:
        cprint("✗ Could not find Kiro binary in extracted files", Colors.RED, bold=True)
        cprint("  Please check the extracted directory manually", Colors.YELLOW)
    else:
        cprint(f"✓ Found binary: {binary_path}", Colors.GREEN)
        
        # Make binary executable
        binary_path.chmod(0o755)
        
        # Create launcher wrapper and desktop entry
        cprint(f"\n🖥️  Setting up desktop integration...", Colors.CYAN)
        launcher_path = create_launcher_wrapper()
        if launcher_path:
            create_desktop_entry(launcher_path)
            # Create symbolic link to launcher wrapper (not binary)
            create_symlink(launcher_path)
        else:
            cprint("⚠ Warning: Could not create launcher wrapper, skipping symlink", Colors.YELLOW)
    
    # Save installed version
    save_installed_version(latest_version)
    
    # Clean up tarball
    cprint(f"\n🧹 Cleaning up tarball...", Colors.CYAN)
    tarball_path.unlink()
    cprint("✓ Tarball removed", Colors.GREEN)
    
    # Success summary
    file_size = sum(f.stat().st_size for f in SCRIPT_DIR.rglob("*") if f.is_file()) / (1024 * 1024)
    cprint(f"\n{'=' * 60}", Colors.GREEN, bold=True)
    cprint(f"✓ Successfully installed Kiro v{latest_version}", Colors.GREEN, bold=True)
    cprint(f"  Location: {SCRIPT_DIR}", Colors.GREEN)
    if binary_path:
        cprint(f"  Binary: {binary_path}", Colors.GREEN)
    cprint(f"  Total size: ~{file_size:.2f} MB", Colors.GREEN)
    cprint(f"{'=' * 60}", Colors.GREEN, bold=True)


if __name__ == "__main__":
    main()
