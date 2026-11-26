# Reel frame study (Trader Vibe Kit)

Per-reel frame/audio/hook measures for ~1,000 Oct trading reels (Drive zips) + ~404 Virlo client reels, correlated with in-account view rank.

- code/analyze_reel.py  one reel -> JSON (+ contact sheet)
- code/run_batch.py     every mp4 in a folder, skips done ones (`res/<stem>.json`)
- code/drive_dl.py      downloads the 71 Drive zips in data/zips.json (folder must be link-shared)
- code/slow_dl.py       Instagram downloads for data/queue.tsv (rate-limited, backs off)
- code/correlate.py     res/ -> study md + csv
- res/                  269 reels already done (skip these)

Needs: python3, ffmpeg, yt-dlp, pip: numpy pandas scipy tabulate opencv-python-headless<5 rapidocr_onnxruntime faster-whisper
