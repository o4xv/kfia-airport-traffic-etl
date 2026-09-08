"""The two official input files and their reference metadata."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
BASE_URL = "https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/"
SOURCE_PAGE = "https://kfia.sa/open-data"
SOURCES = {
    "2024-2025-Open_Data_Domestic.csv": "Domestic",
    "2024-2025-Open_Data_International.csv": "International",
}


def source_url(filename):
    return BASE_URL + "csv/" + filename
