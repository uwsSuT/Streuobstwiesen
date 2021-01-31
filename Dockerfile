# Base Image
FROM python:3.6

# create and set working directory
RUN mkdir /app
RUN mkdir /app/hofverkauf
WORKDIR /app

# Add current directory code to working directory
COPY benutzer /app/benutzer/
COPY hilgi /app/hilgi/
COPY wiese /app/wiese/
COPY obstsorten /app/obstsorten/
COPY hofladen /app/hofladen/
COPY static /app/static/
COPY staticfiles /app/staticfiles/
COPY templates /app/templates/
COPY init_db /app/init_db/
COPY Pipfile /app/
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

# Install system dependencies with OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-setuptools \
        python3-pip \
        python3-venv \
        git \
        gdal-bin \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /app/hilgi/settings.local.py


# install environment dependencies
RUN pip3 install --upgrade pip 
RUN pip3 install pipenv

# Install project dependencies
RUN pipenv install --skip-lock --system --dev

# Expose is NOT supported by Heroku
# EXPOSE 8888
CMD gunicorn hilgi.wsgi:application --bind 0.0.0.0:$PORT
