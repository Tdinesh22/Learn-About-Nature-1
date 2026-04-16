# Learn About Nature Django App

This project includes:

- a home page styled like your reference image
- species pages backed by Django models
- live species listing from the iNaturalist API
- category filtering for birds and insects
- login and signup pages using Django authentication

## Run locally

1. Install dependencies:
   `pip install -r requirements.txt`
2. Create migrations:
   `python manage.py makemigrations`
3. Apply migrations:
   `python manage.py migrate`
4. Load sample species:
   `python manage.py loaddata explore/fixtures/sample_species.json`
5. Start the server:
   `python manage.py runserver`

Open `http://127.0.0.1:8000/`

## iNaturalist API

The species list page reads live taxa from the iNaturalist API.

Read-only species lookup usually works without authentication. If you want to supply an access token, set:

`INATURALIST_ACCESS_TOKEN=your_token_here`

Optional:

`INATURALIST_API_BASE=https://api.inaturalist.org`

Optional version and path:

`INATURALIST_API_VERSION=v2`
`INATURALIST_TAXA_PATH=taxa`

## Admin access

Create an admin user with:

`python manage.py createsuperuser`

Then open `http://127.0.0.1:8000/admin/`
