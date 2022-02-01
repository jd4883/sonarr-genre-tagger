FROM python:alpine3.7
MAINTAINER 'Jacob Dresdale'
LABEL name=sonarr-genre-tagger version=1.6
USER root

VOLUME /config
WORKDIR /config
COPY . /config/
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

ENV \
	SONARR_URL "http://127.0.0.1:8989/api" \
	SONARR_API ""


RUN echo "0 *  *  *  * python /config/main.py" > /etc/crontabs/root && \
    cat /etc/crontabs/root && \
    git clone https://github.com/manami-project/anime-offline-database.git && \
    chmod +x main.py

CMD ["/usr/sbin/crond", "-f", "-d", "8"]
