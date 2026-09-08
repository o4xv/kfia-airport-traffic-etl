"""Lesson 2: compare a text passenger count with its cleaned integer."""
from pathlib import Path

import pandas as pd

file = Path(__file__).resolve().parents[1] / "data" / "raw" / "2024-2025-Open_Data_Domestic.csv"
data = pd.read_csv(file, skiprows=3, nrows=5, encoding="cp1252", dtype="string")

print("Original strings:", data["Pax"].tolist())
without_spaces = data["Pax"].str.strip()
without_commas = without_spaces.str.replace(",", "", regex=False)
passengers = pd.to_numeric(without_commas, errors="raise").astype("Int64")
print("Clean integers:", passengers.tolist())
print("Data type:", passengers.dtype)
print("\nQuestion: why could adding the original strings give the wrong result?")
