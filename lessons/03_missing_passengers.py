"""Lesson 3: unknown is different from zero."""
import pandas as pd

# A tiny example of the source's actual number and missing-value formats.
original = pd.Series([" 1,234 ", " - ", " 0 "], dtype="string")
clean = original.str.strip().replace("-", pd.NA).str.replace(",", "", regex=False)
passengers = pd.to_numeric(clean, errors="raise").astype("Int64")

print(pd.DataFrame({"original": original, "passengers": passengers}).to_string(index=False))
print("Missing values:", passengers.isna().sum())
print("\nQuestion: what claim would filling the unknown with zero make?")
