FROM 		python:alpine3.11
MAINTAINER 	'Jacob Dresdale'
LABEL 		name=sonarr-genre-tagger version=1.6
USER 		root
VOLUME 		/config
WORKDIR 	/config
COPY 		. /config/
RUN 		pip install --upgrade pip && \
			pip install -r requirements.txt && \
			apk add --no-cache git
ENV 		\
			SONARR_URL "http://127.0.0.1:8989/api" \
			SONARR_API "" \
RUN 		git clone https://github.com/manami-project/anime-offline-database.git && \
    		chmod +x main.py
CMD 		["python", "/config/main.py"]
