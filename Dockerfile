FROM debian:latest

ARG DEBIAN_FRONTEND=noninteractive
## Set up libguestfs-tools and dependencies
RUN apt-get -qq update
RUN apt-get -qq install libguestfs-tools jq python3-pip mypy flake8 pylint
RUN pip3 install pyyaml requests tqdm

CMD tail -f /var/log/messages
