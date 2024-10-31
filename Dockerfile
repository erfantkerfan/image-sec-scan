FROM art.azki.com/docker/python:3-alpine3.20
RUN apk update && apk add --no-cache docker-cli grype

WORKDIR /app

COPY main.py ./

CMD ["python", "main.py"]
