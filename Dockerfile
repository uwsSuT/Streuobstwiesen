# Base Image
FROM python:3.7

# create and set working directory
RUN mkdir /app
RUN mkdir /app/hofverkauf
WORKDIR /app


COPY Pipfile /app/
# install environment dependencies
RUN pip3 install --upgrade pip && \
    pip3 install pipenv&& \
    pipenv install --skip-lock --system --dev&& \
    apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        gdal-bin \
	python3-gdal \
        && \
    apt-get purge -y gcc && \
    apt-get purge -y git && \
    apt-get purge -y python2.7 && \
    apt-get purge -y tcl && \
    apt-get purge -y perl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/debconf/* && \
    rm -f /app/hilgi/settings.local.py && \
    useradd uws

# Add current directory code to working directory
COPY benutzer /app/benutzer/
COPY hilgi /app/hilgi/
COPY wiese /app/wiese/
COPY baeume /app/baeume/
COPY obstsorten /app/obstsorten/
COPY hofladen /app/hofladen/
COPY static /app/static/
COPY staticfiles /app/staticfiles/
COPY templates /app/templates/
COPY init_db /app/init_db/
COPY manage.py /app/
COPY schtob /app/schtob/
COPY hofverkauf/Hofverkauf.csv /app/hofverkauf
COPY hofverkauf/hofladen.geojson /app/hofverkauf

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive 

# set project environment variables
# grab these via the Python os.environ
# these are 100% optional here
# $PORT is set by Heroku
ENV PORT=8000

# Schmeiss überflüssige Bilder raus
RUN rm -rf /app/staticfiles/images /root/.cache/* /usr/share/doc/*

# Expose is NOT supported by Heroku
# EXPOSE 8888
#CMD gunicorn hilgi.wsgi:application --bind 0.0.0.0:$PORT
USER uws
CMD uwsgi --module=hilgi.wsgi:application --master --pidfile=/tmp/project-master.pid --http=0.0.0.0:$PORT --socket=/tmp/djnsr.sock --chmod-socket=666
