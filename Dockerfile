FROM debian:latest

ARG DEBIAN_FRONTEND=noninteractive
## Set up libguestfs-tools and dependencies
RUN apt-get -qq update
RUN apt-get -qq install npm libguestfs-tools python3-pip wget
RUN pip3 install pyyaml requests tqdm minio
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc

CMD ["/bin/bash", "tail -f /var/log/messages"]
