#
# Makefile für die Generierung der Streuobstwiesen Docker-App
# einmal local 
# einmal für Heroku
#
## uws : 2020.07.09

VERSION = 0.5.1

LOCAL_PIC_DIR = "static/images/baum"
QGIS_PIC_DIR = "/home/uws/privat/Streuobstwiesen/Bilder/Baum_Bilder/"
WIESEN_NAMES = Buergermeisterwiese \
		        Skater-Tennisplatz\
				Spielplatz\
			   

build_local: 
	- rm Pipfile.lock
	./manage_version.sh $(VERSION)
	cp -p hilgi/settings.local.py hilgi/settings.py
	mkdir -p staticfiles
	HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' \
	python manage.py collectstatic --noinput 
	cp -p Pipfile.local Pipfile
	docker build -t hilgi:$(VERSION) -f Dockerfile-local .

build_heroku:
	- rm Pipfile.lock
	cp -p hilgi/settings.heroku.py hilgi/settings.py
	cp -p Pipfile.heroku Pipfile
	HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' \
	python manage.py collectstatic --noinput
	docker build -t hilgi-docker-obst:$(VERSION) -f Dockerfile .
	heroku container:push web -a hilgi-docker
	heroku config:set HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' -a hilgi-docker
	heroku container:release web -a hilgi-docker
	heroku run python3 manage.py migrate -a hilgi-docker


copy_pics:
	set -x ;\
	actdir=$$(pwd); export actdir ;\
	for d in $(WIESEN_NAMES); do \
		cd $(QGIS_PIC_DIR)/$$d; \
		cp -p $$(cat Nr)*.jpg $${actdir}/$(LOCAL_PIC_DIR)/$$d; \
		cd $${actdir}/$(LOCAL_PIC_DIR)/$$d; \
		for pic in *.jpg; do \
			identify $${pic} | grep "4032x3024" >/dev/null 2>&1; \
			if [ $$? -eq 0 ]; then \
				convert -size 4032x3024 $${pic} -resize 640x480 /tmp/$${pic}; \
				mv /tmp/$${pic} .;\
			fi; \
		done; \
	done
