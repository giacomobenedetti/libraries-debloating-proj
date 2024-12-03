from ubuntu:latest

COPY installed-packages /installed-packages

RUN /usr/lib/dpkg/methods/apt/update /var/lib/dpkg/

RUN dpkg --set-selections < /installed-packages
RUN apt-get dselect-upgrade --yes

CMD ["/bin/bash"]