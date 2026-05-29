# Joey's Movie Crypt - Streamlit Movie Database

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

Open the Local URL on your computer, or the Network URL on your iPhone while both devices are on the same Wi-Fi.

## Files

- `app.py` - the mobile-friendly Streamlit app
- `movie_library.csv` - the enriched movie dataset exported from the workbook
- `requirements.txt` - Python dependencies

## Notes

The app uses the `Cover URL` field directly for poster art. The workbook uses Google Sheets-compatible `=IMAGE(Cover URL)` formulas in the Cover Image column.
