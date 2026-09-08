"""Download original files once, without editing or overwriting them."""
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import urlopen

from sources import BASE_URL, RAW_DIR, SOURCES, source_url


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW_DIR / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    downloads = {name: source_url(name) for name in SOURCES}
    downloads["Meta_Data.xlsx"] = BASE_URL + "Meta_Data.xlsx"

    for filename, url in downloads.items():
        target = RAW_DIR / filename
        if target.exists():
            print(f"Keeping existing original: {filename}")
        else:
            with urlopen(url, timeout=30) as response:
                content = response.read()
            if not content:
                raise ValueError(f"The download was empty: {filename}")
            temporary = target.with_suffix(target.suffix + ".part")
            temporary.write_bytes(content)
            temporary.replace(target)
            manifest[filename] = {
                "url": url,
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            print(f"Downloaded: {filename}")
        # An existing manually downloaded file has no invented download timestamp.
        manifest.setdefault(filename, {"url": url, "downloaded_at_utc": None})
        manifest[filename]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest[filename]["bytes"] = target.stat().st_size
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
