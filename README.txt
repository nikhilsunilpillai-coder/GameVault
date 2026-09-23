GAMEVAULT V7
============
Mini Project I - Game Information & Discovery System

TECH STACK
----------
Frontend: HTML, CSS, JavaScript/Jinja templates
Backend: Python Flask
Database: SQLite

V7 HIGHLIGHTS
-------------
- Admin dashboard with live database statistics
- Searchable admin catalogue
- Add / Edit / Delete game CRUD
- Duplicate-name prevention
- Rating and URL validation
- Platform, language, store and regional-price relationship management
- Game discovery search and filters
- Genre, platform, tag, price and country filtering
- Sorting by name, rating, release date and regional price
- English / Hindi / Marathi interface switcher
- Game detail pages with platforms, languages, pricing and store links
- Responsive layout
- Database cleanup and duplicate prevention from earlier V6 builds
- Image fallback for broken/missing external artwork

IMPORTANT DATABASE NOTE
-----------------------
If you already have a GameVault V6_FIXED3 database with your manually corrected
images (for example Fortnite, EA SPORTS FC 26 and NBA 2K26), copy that existing
file before first run:

V6_FIXED3\database\gamevault.db
        ->
V7\database\gamevault.db

This preserves your existing catalogue and manual edits. Do NOT delete the
existing database if you want to keep your changes.

If you want a completely fresh V7 database, simply leave database/gamevault.db
absent. The application will create and seed it automatically.

RUN
---
V:
cd \GameVault_V7
venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py

Then open:
http://127.0.0.1:5000

ADMIN
-----
http://127.0.0.1:5000/admin

REGIONAL PRICING
----------------
Prices in this academic project are admin-maintained/sample stored values,
not live store prices.

IMAGE SOURCES
-------------
See IMAGE_SOURCES.txt and ARKHAM_SOURCES.txt for catalogue image references.

V7 STATUS
---------
Feature-complete target build. Future work should focus on testing, bug fixes,
documentation, screenshots, presentation and viva preparation rather than
adding unnecessary features.
