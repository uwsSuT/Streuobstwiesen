#
# Makefile für die Generierung der Streuobstwiesen Docker-App
# einmal local 
# einmal für Heroku
#
## uws : 2020.07.09

VERSION = 0.5.2

LOCAL_PIC_DIR = "static/images/baum"
LOCAL_WIESEN_DIR = "static/images/wiese"
QGIS_WIESEN_DIR = "/home/uws/privat/Streuobstwiesen/Bilder"
QGIS_PIC_DIR = "/home/uws/privat/Streuobstwiesen/Bilder/Baum_Bilder"
WIESEN_NAMES = Buergermeisterwiese \
		Skater_Tennisplatz\
		Spielplatz\
		Kunstpfad_Nord\
		Kunstpfad_Ost\
		Feldkreuz\
		Gumpmuehle \
		Bruenndlweg_Richtung_Thalmannsdorf \
		Sportplatz_Bruenndlkapelle \
		Mannrieder_Berg \
		Ferlhof_Kunstpfad \
		MuenchnerStr_West \
		MuenchnerStr_Ost \
		Osterfeuer \
		Stadelham_Gartelsried \



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


copy_wiesen:
	echo "Das geht nur auf dem LAPTOP"
	cp -p $(QGIS_WIESEN_DIR)/[0-9]*_*.png $(LOCAL_WIESEN_DIR)

copy_pics:
	echo "Das geht nur auf dem LAPTOP"
	actdir=$$(pwd); export actdir ;\
    set -x; \
	for wn in $(WIESEN_NAMES); do \
		cd $(QGIS_PIC_DIR)/$$wn; \
		echo "===================================================";\
		echo " Check ob ein Bild neuer ist nur die sollten kopiert werden";\
		echo "====================================================="; \
		for pic in $$(cat Nr)*.jpg; do \
			if [  -e $${actdir}/$(LOCAL_PIC_DIR)/$$wn/$$pic ] && \
			   [ ! $$pic -nt $${actdir}/$(LOCAL_PIC_DIR)/$$wn/$$pic ]; \
			   then \
				echo "PIC $$pic is not newer"; \
				continue; \
			fi; \
			cp -p $$pic $${actdir}/$(LOCAL_PIC_DIR)/$$wn; \
			cd $${actdir}/$(LOCAL_PIC_DIR)/$$wn; \
			identify $${pic} | grep "4032x3024" >/dev/null 2>&1; \
			if [ $$? -eq 0 ]; then \
				convert $${pic} -resize 640x480 /tmp/$${pic}; \
				mv /tmp/$${pic} .;\
			else \
				identify $${pic} | grep "9248x6936" >/dev/null 2>&1; \
				if [ $$? -eq 0 ]; then \
					convert $${pic} -resize 640x480 /tmp/$${pic}; \
					mv /tmp/$${pic} .;\
				fi; \
			fi; \
			cd $(QGIS_PIC_DIR)/$$wn; \
		done; \
	done
