#
# Makefile für die Generierung der Streuobstwiesen Docker-App
# einmal local 
# einmal für Heroku
#
## uws : 2022.01.04
#
# letzte Änderung:
# 04.10.21      Entfernen der Hofläden
#
# 04.01.2022	Hinzufügen der Blühwiesen
#

VERSION = 0.9.1.1

STATIC_IMG_DIR = "static/images"
LOCAL_PIC_DIR = $(STATIC_IMG_DIR)/baum
LOCAL_WIESEN_DIR = $(STATIC_IMG_DIR)/wiese
LOCAL_ACTION_DIR = $(STATIC_IMG_DIR)/aktionen
QGIS_WIESEN_DIR = "/home/uws/privat/Streuobstwiesen/Bilder"
QGIS_PIC_DIR = $(QGIS_WIESEN_DIR)/Baum_Bilder
QGIS_ACTION_DIR = $(QGIS_WIESEN_DIR)/Aktionen
QGIS_BLUEH_PIC_DIR = $(QGIS_WIESEN_DIR)/Bluehwiesen
BLUEH_LOCAL_PIC_DIR = $(STATIC_IMG_DIR)/bluehwiesen

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

BLUEH_WIESEN_NAMES = Feldkreuz_West \
		Kunstpfad_Ost_Kunstobjekte \
		Mannrieder_Berg_Nord \
		Stadelham_Gartelsried_unten \
		Stadelham_Gartelsried_oben \
		Osterfeuer \
		Brünndlhang \
                Wegzwickl_Biotop_Nr._52 \

make_schtob:
	mkdir -p schtob/lib
	cp ../NetWorker_REST_API/schtob/__init__.py schtob
	cp ../NetWorker_REST_API/schtob/nsr_api_defines.py schtob
	cp ../NetWorker_REST_API/schtob/lib/*.py schtob/lib/

build_local: make_schtob
	- rm -f Pipfile.lock
	./manage_version.sh $(VERSION)
	cp -p hilgi/settings.local.py hilgi/settings.py
	mkdir -p staticfiles
	HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' \
	python manage.py collectstatic --noinput 
	cp -p Pipfile.local Pipfile
	docker build -t hilgi:$(VERSION) -f Dockerfile-local .
	rm -rf schtob
	echo "TO Start the new Image run "
	echo "    docker-compose -f docker-compose.yml up "
	echo "    http://localhost:8002"

build_heroku: make_schtob
	- rm -f Pipfile.lock
	./manage_version.sh $(VERSION)
	cp -p hilgi/settings.heroku.py hilgi/settings.py
	cp -p Pipfile.heroku Pipfile
	HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' \
	python manage.py collectstatic --noinput
	docker build -t hilgi-docker-obst:$(VERSION) -f Dockerfile .
	heroku login
	heroku container:login
	heroku container:push web -a hilgi-docker
	heroku config:set HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu' -a hilgi-docker
	heroku container:release web -a hilgi-docker
	heroku run python3 manage.py makemigrations -a hilgi-docker
	heroku run python3 manage.py migrate -a hilgi-docker
	rm -rf schtob
	echo "Go To Heroku ;   heroku run bash -a hilgi-docker"
	echo "python manage.py shell"
	echo "from init_db.initialize import re_init "
	echo "re_init()"

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
		for pic in $$(cat Nr)*.[Jj][Pp][Gg]; do \
			if [  -e $${actdir}/$(LOCAL_PIC_DIR)/$$wn/$$pic ] && \
			   [ ! $$pic -nt $${actdir}/$(LOCAL_PIC_DIR)/$$wn/$$pic ]; \
			   then \
				echo "PIC $$pic is not newer"; \
				continue; \
			fi; \
			cp -p $$pic $${actdir}/$(LOCAL_PIC_DIR)/$$wn; \
			cd $${actdir}/$(LOCAL_PIC_DIR)/$$wn; \
                        convert $${pic} -resize 1024x768 /tmp/$${pic}; \
                        mv /tmp/$${pic} .;\
			cd $(QGIS_PIC_DIR)/$$wn; \
		done; \
	done

copy_blueh_pics:
	echo "Das geht nur auf dem LAPTOP"
	actdir=$$(pwd); export actdir ;\
    set -x; \
	for wn in $(BLUEH_WIESEN_NAMES); do \
		cd $(QGIS_BLUEH_PIC_DIR)/$$wn; \
		echo "===================================================";\
		echo " Check ob ein Bild neuer ist nur die sollten kopiert werden";\
		echo "====================================================="; \
		for pic in $$(cat Nr)*.[Jj][Pp][Gg]; do \
			if [  -e $${actdir}/$(BLUEH_LOCAL_PIC_DIR)/$$wn/$$pic ] && \
			   [ ! $$pic -nt $${actdir}/$(BLUEH_LOCAL_PIC_DIR)/$$wn/$$pic ]; \
			   then \
				echo "PIC $$pic is not newer"; \
				continue; \
			fi; \
			cp -p $$pic $${actdir}/$(BLUEH_LOCAL_PIC_DIR)/$$wn; \
			cd $${actdir}/$(BLUEH_LOCAL_PIC_DIR)/$$wn; \
                        convert $${pic} -resize 1024x768 /tmp/$${pic}; \
                        mv /tmp/$${pic} .;\
			cd $(QGIS_BLUEH_PIC_DIR)/$$wn; \
		done; \
	done

copy_action_pics:
	echo "Das geht nur auf dem LAPTOP"
	actdir=$$(pwd); export actdir ;\
    set -x; \
	cd $(QGIS_ACTION_DIR); \
	echo "===================================================";\
	echo " Check ob ein Bild neuer ist nur die sollten kopiert werden";\
	echo "====================================================="; \
	for pic in 2022/*.jpg; do \
		if [  -e $${actdir}/$(LOCAL_ACTION_DIR)/$$pic ] && \
		   [ ! $$pic -nt $${actdir}/$(LOCAL_ACTION_DIR)/$$pic ]; \
		   then \
			echo "PIC $$pic is not newer"; \
			continue; \
		fi; \
		cp -p $$pic $${actdir}/$(LOCAL_ACTION_DIR)/$$(dirname $$pic); \
		cd $${actdir}/$(LOCAL_ACTION_DIR); \
		identify $${pic} | grep "4032x3024" >/dev/null 2>&1; \
		if [ $$? -eq 0 ]; then \
                    convert $${pic} -resize 1024x768 /tmp/$$(basename $$pic); \
                    mv /tmp/$$(basename $$pic) ./$$(dirname $$pic) ;\
		elif [ identify $${pic} | grep "9248x6936" >/dev/null 2>&1 ]; then \
                    convert $${pic} -resize 1024x768 /tmp/$$(basename $$pic); \
                    mv /tmp/$$(basename $$pic) ./$$(dirname $$pic);\
		else \
                    convert $${pic} -resize 1024x768 /tmp/$$(basename $$pic); \
                    mv /tmp/$$(basename $$pic) ./$$(dirname $$pic);\
		fi; \
		cd $(QGIS_ACTION_DIR); \
	done; \
