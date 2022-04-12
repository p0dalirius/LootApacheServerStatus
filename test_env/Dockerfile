FROM debian:buster

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq -y update; \
    apt-get -qq -y install software-properties-common curl apache2; \
    rm /var/www/html/index.*

RUN a2enmod status ;\
    sed -i 's/Require local//g' /etc/apache2/mods-enabled/status.conf ;\
    service apache2 start ;\
    service apache2 stop

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]