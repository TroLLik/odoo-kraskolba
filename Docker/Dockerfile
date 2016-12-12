# My Odoo Dockerfile
# VERSION 0.1
# AUTHOR:         TroLL <z@kspu.ru>
# DESCRIPTION:    Image for Odoo
# TO_BUILD:       eatmydata docker build --tag=prod/kkolba-odoo-v0.1 .
# TO_RUN:         docker run -d -p 8069 --restart=always --name kkolba-odoo-prox -v=/opt/docker/kkolba-odoo/odoo-kraskolba:/mnt/proj:ro -v=/opt/docker/kkolba-odoo/log:/mnt/log:rw -v=/opt/docker/kkolba-odoo/odoo.conf:/etc/odoo.conf:ro prod/kkolba-odoo-v0.1 /start
# TO_PROX_RUN:    docker run -d --restart=always --name kkolba-odoo-prox -v=/opt/docker/kkolba-odoo/odoo-kraskolba:/mnt/proj:ro -v=/opt/docker/kkolba-odoo/log:/mnt/log:rw -v=/opt/docker/kkolba-odoo/odoo.conf:/etc/odoo.conf:ro prod/kkolba-odoo-v0.1 /start

FROM ubuntu:14.04
MAINTAINER TroLL <z@kspu.ru>

# Install some deps, lessc and less-plugin-clean-css, other odoo deps and wkhtmltopdf
RUN set -x; \
        apt-get update && apt-get upgrade -y \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            node-less \
            node-clean-css \
            python-pyinotify \
            python-renderpm \
            python-support \
            python-cups python-dateutil python-decorator python-docutils python-feedparser \
            python-gdata python-geoip python-gevent python-imaging python-jinja2 python-ldap python-libxslt1 \
            python-lxml python-mako python-mock python-openid python-passlib python-psutil python-psycopg2 \
            python-pybabel python-pychart python-pydot python-pyparsing python-pypdf python-reportlab python-requests \
            python-simplejson python-tz python-unicodecsv python-unittest2 python-vatnumber python-vobject \
            python-werkzeug python-xlwt python-yaml wkhtmltopdf git python-setuptools python-genshi python-cairo python-lxml \
            python-pip \
        && curl -o wkhtmltox.deb -SL http://nightly.odoo.com/extra/wkhtmltox-0.12.1.2_linux-jessie-amd64.deb \
        && echo '40e8b906de658a2221b15e4e8cd82565a47d7ee8 wkhtmltox.deb' | sha1sum -c - \
        && dpkg --force-depends -i wkhtmltox.deb \
        && apt-get -y install -f --no-install-recommends \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false npm \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Make sure we don't get notifications we can't answer during building.
ENV    DEBIAN_FRONTEND noninteractive

# # add odoo files
# ADD ./odoo /opt/odoo

#clone odoo
RUN git clone https://www.github.com/odoo/odoo --depth 1 --branch 8.0 --single-branch /opt/odoo

VOLUME ["/mnt/proj", "/mnt/log"]

#add user odoo
RUN adduser --system --home=/opt/odoo -u 1488 --group odoo

#chown to odoo user
RUN chown -R odoo:odoo /opt/odoo
RUN chown -R odoo:odoo /mnt/proj
RUN chown -R odoo:odoo /mnt/log

#clone external odoo deps
RUN git clone https://github.com/aeroo/aeroo_reports.git /opt/ext_addons/aeroo_reports
RUN git clone https://github.com/aeroo/aeroolib.git /opt/ext_addons/aeroolib
RUN git clone https://github.com/codup/odoo-tools.git /opt/ext_addons/codup

#setup odoo aeroolib
RUN cd /opt/ext_addons/aeroolib/ && python setup.py install

#install pwgen for python
RUN pip install pwgen

# Expose Odoo services
EXPOSE 8069

# Copy start script
COPY ./start /

# Fix exec permission
RUN chmod +x /start

# Set default user when running the container
USER odoo

CMD ["/start"]