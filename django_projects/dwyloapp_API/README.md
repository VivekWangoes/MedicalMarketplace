# Dwylo App


## Set up DEV environmant
```shell
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## for postgress db creation
	sudo -u postgres psql
	postgres=# create database dwylo_app;
	postgres=# create user dwylo_user with encrypted password 'dwylo_pass';
	postgres=# grant all privileges on database dwylo_app to dwylo_user;


## for table creation
	python manage.py makemigrations
	python manage.py migrate

## run command to run server
	# go to project dir and run
	python manage.py runserver


# EMAIL CONFIGURATION
## Add your email and password in virtual environment
	## EMAIL_HOST_USER = "dwylo@gmail.com"
	## EMAIL_HOST_PASSWORD = "12345"


# Way to set data in virtual environment
	export EMAIL_HOST_USER=safebeat@gmail.com EMAIL_HOST_PASSWORD=safebeato@123 DB_NAME=dwylo_app DB_USER=dwylo_user DB_PASSWORD=dwylo_pass DB_HOST=localhost

# API COLLECTION LINK
	(https://documenter.getpostman.com/view/11889792/UVeMJ3we)