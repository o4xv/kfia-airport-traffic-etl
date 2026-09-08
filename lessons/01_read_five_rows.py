"""Lesson 1: read five rows. No database or cleaning yet."""
import pandas as pd

# This path starts from the project folder you opened in VS Code.
file = "data/raw/2024-2025-Open_Data_Domestic.csv"

# The source has three empty rows before the header and eight meaningful columns.
data = pd.read_csv(file, skiprows=3, usecols=range(1, 9), nrows=5,
                   encoding="cp1252", dtype="string", keep_default_na=False)

print(data.to_string(index=False))
print("\nRows and columns:", data.shape)
print("\nQuestion: does one row represent one flight or a monthly summary?")
