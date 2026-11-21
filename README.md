# Lakdi Aadhat Website (Django)

## 1. One-time setup on your Mac
```bash
brew install python git
cd lakdi_aadhat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations accounts core trade
python manage.py migrate
python manage.py createsuperuser      # this becomes the Owner login
python manage.py runserver
```
Open http://127.0.0.1:8000 (site) and http://127.0.0.1:8000/admin (admin).

## 2. First data to enter in /admin
1. Core -> Wood rates (poplar, eucalyptus ... with today's rate)
2. Trade -> Parties: add suppliers (UP) and buyers (factories). For a factory that should log in,
   register it from the site, approve it in Accounts -> Profiles, then link the user in its Party record.
3. Make staff accounts: create user -> Profile role = STAFF, Approved = ticked.
4. Then use the Portal (/portal/) to add trucks, weighments, payments.

## 3. Switch to PostgreSQL (recommended before going live)
```bash
brew install postgresql@16 && brew services start postgresql@16
createdb lakdi
export DB_NAME=lakdi DB_USER=$(whoami)
python manage.py migrate
```

## 4. Edit business details
`config/settings.py` -> BUSINESS = {...} (name, phone, WhatsApp number, address).

## 5. Deploy later
Push to GitHub, then Render / Railway or a VPS.
Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
Start: `gunicorn config.wsgi`
Set env vars: DJANGO_SECRET_KEY, DJANGO_DEBUG=0, DJANGO_ALLOWED_HOSTS=yourdomain.com,
DJANGO_CSRF_ORIGINS=https://yourdomain.com, and the DB_* values.
NOTE: uploaded slip photos need persistent storage (a disk or S3) on cloud hosts.
