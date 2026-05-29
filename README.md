# Joey's Movie Crypt - Streamlit Movie Database

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

Open the Local URL on your computer, or the Network URL on your iPhone while both devices are on the same Wi-Fi.

## Views

- **VHS Shelf**: larger movie cards with poster, details, and optional overview.
- **Poster Grid**: compact scrollable poster wall for iPhone browsing.

## Filters

Use the sidebar to filter by:

- Search text
- Watched status
- One or more genres
- Genre match mode: any selected genre or all selected genres
- Format
- Sort order

## Files

- `app.py` - the mobile-friendly Streamlit app
- `movie_library.csv` - the enriched movie dataset exported from the workbook
- `requirements.txt` - Python dependencies

## Notes

The app uses native Streamlit image rendering with fallback support for `Cover URL`, `Poster Path`, and Google Sheets `=IMAGE()` formulas in the Cover Image column.
