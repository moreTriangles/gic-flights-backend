python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=flaskr
export FLASK_ENV=development
flask init-db
flask run