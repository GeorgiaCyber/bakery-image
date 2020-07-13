FROM debian:latest

ARG DEBIAN_FRONTEND=noninteractive
## Set up libguestfs-tools and dependencies
RUN apt-get -qq update
RUN apt-get -qq install npm libguestfs-tools

CMD ["/bin/bash", "tail -f /var/log/messages"]
