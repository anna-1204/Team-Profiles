# Team Profile App

A Streamlit app that auto-renders employee profiles from an Excel sheet, grouped by level (L3 → L2 → L1) and role hierarchy.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Folder Structure

```
profile_app/
├── app.py
├── requirements.txt
├── Profile details.xlsx        ← edit this to update profiles
└── images/
    ├── Ankit.jpg
    ├── Krishna.jpg
    ├── Madhushree Honnappa.jpg
    ├── Manoj.jpg
    ├── Yamini.png
    └── ...                     ← add more photos here
```

## Excel Columns (do not rename)

| Column | Description |
|--------|-------------|
| `Full name` | Person's full name |
| `KTLO Designation` | Must start with level prefix: `L3,`, `L2,`, `L1` |
| `One / Two Liner Current JD` | Job description (bullet-separated with • or newlines) |
| `Certification Details` | (optional, not displayed) |
| `Profile Photo (Professional)` | Just the filename, e.g. `Ankit.jpg` |

## Level & Role Hierarchy

**Levels** (top → bottom): L3 → L2 → L1

**Role order within each level:**
1. Technical Lead
2. Module Lead
3. Senior SharePoint Consultant
4. SharePoint Consultant
5. SharePoint Support Engineer
6. Senior Software Design Engineer (SSDE)
7. Software Design Engineer
8. COTS KTLO Support & GLE2E Dev System support
9. Senior Software Design Engineer, COTS KTLO Support & GLE2E Dev System support

## Adding Photos

1. Place the image file in the `images/` folder
2. Enter **exactly** the filename (including extension) in the Excel `Profile Photo` column
3. Refresh the app

If an image is missing or not found, a grey placeholder silhouette is shown automatically.
