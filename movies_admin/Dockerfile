FROM python:3.8.10

ARG config=dev
ARG workdir=/opt/app

ADD requirements/ $workdir/requirements
WORKDIR $workdir

RUN pip3 install -r requirements/$config.txt
ADD . $workdir

RUN mkdir $workdir/staticfiles
RUN python manage.py collectstatic --no-input --clear

RUN useradd -ms /bin/bash app && chown -R app $workdir
USER app

CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000