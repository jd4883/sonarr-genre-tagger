FROM python:alpine3.7
MAINTAINER 'Jacob Dresdale'
LABEL name=sonarr-genre-tagger version=1.6
USER root

VOLUME /config
WORKDIR /config
COPY requirements.txt /config/
RUN pip install --upgrade pip && \
	pip install -r requirements.txt && \
	apk add --no-cache bash \
		openssh \
		libc6-compat \
		util-linux \
		pciutils \
		usbutils \
		coreutils \
		binutils \
		findutils \
		grep \
        git

ARG \
	FREQUENCY=3 \
	APPEND_TO_CRON_END=""

ENV \
	SONARR_URL "http://127.0.0.1:8989/api" \
	SONARR_API "" \
	FREQUENCY ${FREQUENCY} \
	APPEND_TO_CRON_END  ${APPEND_TO_CRON_END}

COPY . /config/
RUN echo "0 */${FREQUENCY} * * * python /config/main.py ${APPEND_TO_CRON_END}"
RUN echo "0 */${FREQUENCY} * * * python /config/main.py ${APPEND_TO_CRON_END}" > /etc/crontabs/root && \
    cat /etc/crontabs/root && \
    git clone https://github.com/manami-project/anime-offline-database.git && \
    chmod +x main.py

CMD ["/usr/sbin/crond", "-f", "-d", "8"]
