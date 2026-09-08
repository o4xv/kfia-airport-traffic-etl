# Start here: one small lesson

The complete project is available, but your first session uses only `lessons/01_read_five_rows.py`. Leave the database and the complete ETL script for later sessions.

## Today's purpose

Understand how pandas reads a CSV and what one source row represents. The prepared local copy already has Python packages and the original files downloaded.

1. Open the **kfia-airport-traffic-etl** folder in VS Code.
2. Open `lessons/01_read_five_rows.py`.
3. Open a terminal in that project folder and run:

```powershell
.\.venv\Scripts\python.exe lessons\01_read_five_rows.py
```

The result should have **5 rows and 8 columns**. All five rows concern domestic arrivals associated with Abha in 2025:

| Month | Passengers | Flights |
| --- | ---: | ---: |
| Jan | 20,359 | 132 |
| Feb | 17,561 | 117 |
| Mar | 15,262 | 122 |
| Apr | 23,333 | 150 |
| May | 22,267 | 162 |

The original city text contains an extra trailing character. Depending on terminal encoding it may display as `Abhaÿ` or a replacement symbol. We will inspect and correct that later, while retaining the original source file.

## Read just these ideas

`import pandas as pd` makes the pandas library available under the short name `pd`.

`pd.read_csv(...)` reads a CSV into a **DataFrame**, which is a table held in Python's memory. The variable `data` refers to that table.

The arguments describe this particular source: `skiprows=3` skips its empty opening rows, `usecols=range(1, 9)` selects its eight meaningful columns, and `nrows=5` reads a small sample. `encoding="cp1252"` decodes the source bytes. `dtype="string"` keeps values as text until we decide how to clean them.

`data.shape` returns the number of rows and columns. We expect `(5, 8)`.

## Your small exercise

Change `nrows=5` to `nrows=3`, predict the shape, and run the lesson again. Restore it to 5 afterward.

Write your own completion of this sentence:

> One row represents the total passengers and flights for ______.

Also explain whether `132` means this is one flight or a summary of many flights.

That is enough for the first session. Share your output and explanation when you want feedback. Next comes [cleaning one passenger column](lessons/02_clean_passengers.py).
