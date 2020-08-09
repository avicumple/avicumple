FROM debian:9.11

WORKDIR /django

COPY www/appcumple/requirements.txt ./
RUN set -ex \
	&& buildDeps=" \
		build-essential \
		libssl-dev \
		libgmp-dev \
		pkg-config \
		" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get install -y python python-dev python-pip python-setuptools \
    && apt-get install -y libssl-dev libcurl4-openssl-dev \
    && apt-get install -y imagemagick libmagickwand-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/* \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

COPY . .

WORKDIR /django/www/appcumple

# This is necessary to be able to find "_filtro.so" module
ENV PYTHONPATH /django/www/appcumple/avicumple

RUN python manage.py syncdb --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]