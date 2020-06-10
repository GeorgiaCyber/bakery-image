FROM debian:latest


## Set up libguestfs-tools and dependencies
RUN apt-get -qq update
RUN apt-get -qq install libguestfs-tools jq

CMD tail -f /var/log/messages
