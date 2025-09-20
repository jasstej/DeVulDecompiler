#!/usr/bin/env python3
import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("Pillow is required. Install with: pip install pillow", file=sys.stderr)
    sys.exit(1)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def to_square(image: Image.Image, background=(0, 0, 0, 0)) -> Image.Image:
    w, h = image.size
    if w == h:
        return image
    side = max(w, h)
    mode = "RGBA" if image.mode in ("RGBA", "LA") else "RGB"
    bg = Image.new(mode, (side, side), background)
    offset = ((side - w) // 2, (side - h) // 2)
    bg.paste(image, offset, image if image.mode in ("RGBA", "LA") else None)
    return bg


def save_resized_square(src_img: Image.Image, size: int, out_path: str) -> None:
    img = to_square(src_img)
    img = img.resize((size, size), Image.LANCZOS)
    img.save(out_path, format="PNG", optimize=True)
    print(f"Wrote {out_path} ({size}x{size})")


def save_logo_small(src_img: Image.Image, out_path: str, existing_small: str) -> None:
    target_h = 48
    if os.path.exists(existing_small):
        try:
            with Image.open(existing_small) as old:
                target_h = old.height
        except Exception:
            pass

    w, h = src_img.size
    scale = target_h / float(h)
    target_w = max(1, int(round(w * scale)))
    resized = src_img.resize((target_w, target_h), Image.LANCZOS)
    resized.save(out_path, format="PNG", optimize=True)
    print(f"Wrote {out_path} (~{target_w}x{target_h})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DeVul brand assets from a source image")
    parser.add_argument("--input", required=True, help="Path to the high-res logo image (PNG recommended)")
    parser.add_argument(
        "--out-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "static", "img"),
        help="Output directory for generated PNGs (default: static/img)",
    )
    args = parser.parse_args()

    src_path = os.path.abspath(args.input)
    out_dir = os.path.abspath(args.out_dir)
    ensure_dir(out_dir)

    if not os.path.exists(src_path):
        print(f"Source image not found: {src_path}", file=sys.stderr)
        return 2

    try:
        with Image.open(src_path) as im:
            # Convert to RGBA to preserve transparency if available
            if im.mode not in ("RGBA", "LA"):
                im = im.convert("RGBA")

            # Primary outputs (keep filenames used by templates/manifest)
            save_logo_small(
                im,
                out_path=os.path.join(out_dir, "devul-logo-small.png"),
                existing_small=os.path.join(out_dir, "devul-logo-small.png"),
            )
            save_resized_square(im, 16, os.path.join(out_dir, "devul-favicon-16x16.png"))
            save_resized_square(im, 32, os.path.join(out_dir, "devul-favicon-32x32.png"))
            save_resized_square(im, 192, os.path.join(out_dir, "devul-favicon-192x192.png"))
            save_resized_square(im, 180, os.path.join(out_dir, "devul-apple-touch-icon.png"))

    except Exception as e:
        print(f"Failed to process image: {e}", file=sys.stderr)
        return 3

    print("All assets generated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
