# NOT FINISED!

# Intention: Build a Dockerfile to facilitate Flask, Python3 and Nginx with UWSGI

FROM alpine

# Install Alpine packages
RUN apk update -qq \
        && apk upgrade \
        && apk add --no-cache python3 py3-pip nginx sqlite pcre-dev uwsgi-python3

# Install Python3 packages
RUN pip install \
        flask \
        unidecode

# Expose ports
EXPOSE 80
EXPOSE 443

