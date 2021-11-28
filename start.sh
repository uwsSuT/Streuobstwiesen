export PYTHONPATH=~/GIT_projects/NetWorker_REST_API
export HILGI_SEC_KEY='qt+*4)txyz(_=0f*(p6v-jbl+x7!eb*o^6lracku7ym@#!kpcu'
export DEBUG=1
export ALLOWED_HOST=localhost
gunicorn hilgi.wsgi:application --bind 0.0.0.0:8004
