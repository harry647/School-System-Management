#!/usr/bin/env python3
"""
Icon conversion script for School System Management.

Converts PNG icons to ICO format for Windows installer compatibility.
"""

import os
from pathlib import Path
from PIL import Image

def convert_png_to_ico(png_path, ico_path, sizes=None):
    """
    Convert PNG file to ICO format with multiple sizes.

    Args:
        png_path: Path to input PNG file
        ico_path: Path to output ICO file
        sizes: List of sizes to include (default: [16, 32, 48, 64, 128, 256])
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]

    print(f"Converting {png_path} to {ico_path}")

    try:
        # Open the PNG image
        img = Image.open(png_path)

        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create ICO file with multiple sizes
        icons = []
        for size in sizes:
            # Resize image maintaining aspect ratio
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO
        icons[0].save(
            ico_path,
            format='ICO',
            sizes=[(icon.size[0], icon.size[1]) for icon in icons],
            append_images=icons[1:]
        )

        print(f"[SUCCESS] Created ICO file with sizes: {[f'{s}x{s}' for s in sizes]}")
        return True

    except Exception as e:
        print(f"[ERROR] Error converting icon: {e}")
        return False

def main():
    """Main conversion function."""
    project_root = Path(__file__).parent

    # Define icon conversions
    conversions = [
        {
            'png': project_root / 'school_system' / 'gui' / 'resources' / 'icons' / 'logo.png',
            'ico': project_root / 'school_system' / 'gui' / 'resources' / 'icons' / 'logo.ico'
        }
    ]

    success_count = 0

    for conv in conversions:
        if conv['png'].exists():
            success = convert_png_to_ico(conv['png'], conv['ico'])
            if success:
                success_count += 1
        else:
            print(f"[ERROR] Source PNG not found: {conv['png']}")

    print(f"\nConversion complete: {success_count}/{len(conversions)} icons converted")

    if success_count == len(conversions):
        print("[SUCCESS] All icons converted successfully")
        return True
    else:
        print("[ERROR] Some icons failed to convert")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)