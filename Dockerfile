ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apk update && apk add --no-cache docker-cli grype

WORKDIR /app

COPY main.py ./

CMD ["python", "main.py"]
