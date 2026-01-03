# ytgrab

a simple youtube to mp3 cli tool that actually keeps your metadata intact.


## what it does

- grabs audio from youtube, converts to mp3
- embeds the thumbnail as album art
- preserves title, artist, channel as id3 tags
- quality options from 128-320 kbps

## requirements

- python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/download.html)

## install

```bash
pip install yt-dlp
```

ffmpeg needs to be installed separately and in your PATH:
- windows: `winget install ffmpeg` or download from ffmpeg.org
- mac: `brew install ffmpeg`
- linux: `sudo apt install ffmpeg`

## usage

**cli:**
```bash
python ytgrab.py <url>
python ytgrab.py <url> -q 320          # max quality
python ytgrab.py <url> -o ./music      # custom output folder
python ytgrab.py <url> --info-only     # just show video info
```

**or just double-click `ytgrab.bat`** and paste your url. ez.

## options

| flag | what it does |
|------|--------------|
| `-o, --output` | where to save (default: ./downloads) |
| `-q, --quality` | bitrate: 128, 192, 256, 320 (default: 192) |
| `--keep-thumbnail` | save thumbnail as separate file |
| `--info-only` | preview metadata without downloading |
| `-v, --verbose` | show all the yt-dlp output |

## legal stuff

this is for archiving content you have the right to download - your own uploads, creative commons stuff, public domain lectures, etc.


## license

mit - do whatever you want
