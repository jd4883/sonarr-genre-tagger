FROM 		--platform=linux/amd64 python:alpine3.11
MAINTAINER 	'Jacob Dresdale'
LABEL 		name=sonarr-genre-tagger version=1.7
USER 		root
VOLUME 		/config
WORKDIR 	/config
COPY 		. /config/
RUN 		pip install --upgrade pip && \
			pip install -r requirements.txt && \
			apk add --no-cache bash \
				openssh \
				git
ENV 		\
			SONARR_URL "http://127.0.0.1:8989/api" \
			SONARR_API "" \
			GIT_SSH_COMMAND "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
RUN 		chmod +x main.py
CMD 		["python", "/config/main.py"]
