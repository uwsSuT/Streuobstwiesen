#
# Makefile für die Generierung der Streuobstwiesen Docker-App
# einmal local 
# einmal für Heroku
#
## uws : 2020.07.09

VERSION = 0.5.0

build_local: 
	- rm Pipfile.lock
	python manage.py collectstatic --noinput 
	cp -p hilgi/settings.local.py hilgi/settings.py
	cp -p Pipfile.local Pipfile
	docker build -t hilgi:$(VERSION) -f Dockerfile-local .

build_heroku:
	- rm Pipfile.lock
	cp -p hilgi/settings.heroku.py hilgi/settings.py
	cp -p Pipfile.heroku Pipfile
	python manage.py collectstatic --noinput
	docker build -t hilgi-docker-obst:$(VERSION) -f Dockerfile .
	heroku container:push web -a hilgi-docker
	heroku config:set HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu'
	heroku container:release web -a hilgi-docker
	heroku run python3 manage.py migrate -a hilgi-docker
