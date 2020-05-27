FROM python:3.7
WORKDIR /usr/src/app

COPY . .
RUN pip3 install -r requirements.txt
CMD ["make","spider"]

# environment variables
# DYNACONF_NAME 
# DYNACONF_ALLOWED_DOMAINS
# DYNACONF_START_URLS='@json ["baserul", "baseurl2"]'