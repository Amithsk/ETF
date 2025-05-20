import os
import shutil
import subprocess
from datetime import datetime

# --- Step 1: Run the download script ---
download_script = "/home/amith/ETF/ETF_Extract/NSE_ETF_Daily_Downloader.py"
os.system(f"python3 {download_script}")
print("Download script executed.")

# --- Step 2: Move the downloaded file and delete from source ---
src_folder = "/home/amith/"
dst_folder = "/home/amith/ETF/ETF_Data/Download"

# Find the newest file in the source folder specifically check for csv
files = sorted(
    [f for f in os.listdir(src_folder)
     if os.path.isfile(os.path.join(src_folder, f))
     and f.startswith("ETF_")
     and f.endswith(".csv")],
    key=lambda x: os.path.getmtime(os.path.join(src_folder, x)),
    reverse=True
)

if files:
    latest_file = files[0]
    src_file = os.path.join(src_folder, latest_file)
    dst_file = os.path.join(dst_folder, latest_file)

    # Copy to Git folder
    shutil.copy2(src_file, dst_file)
    print(f"Copied {latest_file} to Git folder.")

    # --- Step 3: Git commit and push ---
    os.chdir("/home/amith/ETF/ETF_Data")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Add new ETF file: {latest_file}"], check=False)
    subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=False)

    # Delete original
    os.remove(src_file)
    print(f"Deleted {latest_file} from source folder.")
else:
    print("No new ETF files found to move.")
