#!/usr/bin/env python3
"""
ytgrab - A metadata-preserving YouTube to MP3 CLI tool.

This tool is designed for archival and educational purposes for content
the user has a legal right to access offline. It preserves all available
metadata (title, artist, album, thumbnail) embedded in the output file.

Usage:
    python ytgrab.py <youtube_url> [options]
    python ytgrab.py --help
"""

import argparse
import os
import sys
import subprocess
import json
import re
from pathlib import Path


def check_dependencies():
    """Check if yt-dlp and ffmpeg are installed."""
    missing = []
    
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("yt-dlp")
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("ffmpeg")
    
    if missing:
        print(f"[ERROR] Missing dependencies: {', '.join(missing)}")
        print("\nInstall them with:")
        if "yt-dlp" in missing:
            print("  pip install yt-dlp")
        if "ffmpeg" in missing:
            print("  Download from https://ffmpeg.org/download.html")
        sys.exit(1)


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename."""
    # Remove characters that are invalid in Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Limit length
    return sanitized[:200] if len(sanitized) > 200 else sanitized


def get_video_info(url: str) -> dict:
    """Fetch video metadata using yt-dlp."""
    print("[INFO] Fetching video metadata...")
    
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to fetch video info: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse video metadata")
        sys.exit(1)


def download_audio(url: str, output_dir: Path, quality: str = "192", 
                   keep_thumbnail: bool = False, verbose: bool = False) -> Path:
    """
    Download audio from YouTube and convert to MP3 with embedded metadata.
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save the file
        quality: Audio bitrate (e.g., "128", "192", "320")
        keep_thumbnail: Keep the thumbnail as a separate file
        verbose: Show yt-dlp output
    
    Returns:
        Path to the downloaded MP3 file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Output template - yt-dlp will handle the filename
    output_template = str(output_dir / "%(title)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        # Audio extraction
        "-x",                           # Extract audio
        "--audio-format", "mp3",        # Convert to MP3
        "--audio-quality", f"{quality}K",  # Bitrate
        
        # Metadata preservation
        "--embed-thumbnail",            # Embed thumbnail as album art
        "--embed-metadata",             # Embed all available metadata
        "--add-metadata",               # Add metadata to file
        
        # Additional metadata options
        "--parse-metadata", "%(title)s:%(meta_title)s",
        "--parse-metadata", "%(uploader)s:%(meta_artist)s",
        "--parse-metadata", "%(channel)s:%(meta_album_artist)s",
        
        # Thumbnail processing (ffmpeg will handle embedding)
        "--convert-thumbnails", "jpg",  # Convert thumbnail to jpg for compatibility
        
        # Output
        "-o", output_template,
        
        # Don't re-download if exists
        "--no-overwrites",
        
        # URL
        url
    ]
    
    if keep_thumbnail:
        cmd.insert(-1, "--write-thumbnail")
    
    if not verbose:
        cmd.insert(1, "-q")  # Quiet mode
        cmd.insert(2, "--progress")  # But show progress
    
    print(f"[INFO] Downloading and converting to MP3 ({quality}kbps)...")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Download failed: {e}")
        sys.exit(1)
    
    # Find the output file (yt-dlp creates it)
    mp3_files = list(output_dir.glob("*.mp3"))
    if mp3_files:
        # Return the most recently modified mp3
        return max(mp3_files, key=lambda p: p.stat().st_mtime)
    
    print("[ERROR] MP3 file not found after download")
    sys.exit(1)


def display_metadata(filepath: Path):
    """Display the embedded metadata using ffprobe."""
    print("\n[INFO] Embedded Metadata:")
    print("-" * 40)
    
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(filepath)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tags = data.get("format", {}).get("tags", {})
        
        if tags:
            for key, value in tags.items():
                # Clean up the key name
                display_key = key.replace("_", " ").title()
                print(f"  {display_key}: {value}")
        else:
            print("  No metadata tags found")
            
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print("  (Could not read metadata - ffprobe may not be available)")
    
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        prog="ytgrab",
        description="A metadata-preserving YouTube to MP3 CLI tool for archival purposes.",
        epilog="Example: python ytgrab.py https://youtube.com/watch?v=VIDEO_ID -o ./music"
    )
    
    parser.add_argument(
        "url",
        help="YouTube video URL to download"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("./downloads"),
        help="Output directory (default: ./downloads)"
    )
    
    parser.add_argument(
        "-q", "--quality",
        choices=["128", "192", "256", "320"],
        default="192",
        help="Audio quality/bitrate in kbps (default: 192)"
    )
    
    parser.add_argument(
        "--keep-thumbnail",
        action="store_true",
        help="Keep thumbnail as a separate image file"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed yt-dlp output"
    )
    
    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Only show video info, don't download"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    # Validate URL (basic check)
    if "youtube.com" not in args.url and "youtu.be" not in args.url:
        print("[WARNING] URL doesn't appear to be a YouTube link. Proceeding anyway...")
    
    # Info only mode
    if args.info_only:
        info = get_video_info(args.url)
        print("\n[VIDEO INFO]")
        print(f"  Title: {info.get('title', 'Unknown')}")
        print(f"  Channel: {info.get('channel', 'Unknown')}")
        print(f"  Uploader: {info.get('uploader', 'Unknown')}")
        print(f"  Duration: {info.get('duration_string', 'Unknown')}")
        print(f"  Upload Date: {info.get('upload_date', 'Unknown')}")
        print(f"  View Count: {info.get('view_count', 'Unknown'):,}")
        print(f"  Description: {info.get('description', 'None')[:200]}...")
        return
    
    # Download
    print(f"\n{'='*50}")
    print("  ytgrab - YouTube to MP3 Archival Tool")
    print(f"{'='*50}\n")
    
    output_file = download_audio(
        url=args.url,
        output_dir=args.output,
        quality=args.quality,
        keep_thumbnail=args.keep_thumbnail,
        verbose=args.verbose
    )
    
    print(f"\n[SUCCESS] Downloaded: {output_file.name}")
    print(f"[SUCCESS] Location: {output_file.absolute()}")
    
    # Display embedded metadata
    display_metadata(output_file)
    
    print("\n[DONE] Download complete!")


if __name__ == "__main__":
    main()
