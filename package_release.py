"""
Helper script to package the compiled distribution into a ready-to-upload GitHub Release ZIP.
"""
import os
import shutil
import zipfile

def package():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_folder = os.path.join(root_dir, "dist", "yt-dlp-gui")
    output_zip = os.path.join(root_dir, "dist", "yt-dlp-gui-windows-x64.zip")

    if not os.path.isdir(dist_folder):
        print(f"ERROR: Build folder not found at {dist_folder}")
        print("Please run 'python build_exe.py' first!")
        return

    print("==================================================")
    print("Packaging yt-dlp & FFmpeg GUI for GitHub Releases")
    print("==================================================")
    print(f"Source folder: {dist_folder}")
    print(f"Creating archive: {output_zip}...")

    if os.path.isfile(output_zip):
        os.remove(output_zip)

    # Create zip archive
    shutil.make_archive(
        base_name=os.path.splitext(output_zip)[0],
        format="zip",
        root_dir=dist_folder
    )

    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"\nSUCCESS! Package created: {output_zip}")
    print(f"Archive Size: {size_mb:.1f} MB")
    print("\nYou can now upload this zip file directly to GitHub Releases:")
    print("https://github.com/hazynyx/yt-mpeg-gui/releases/new")
    print("==================================================")

if __name__ == "__main__":
    package()
