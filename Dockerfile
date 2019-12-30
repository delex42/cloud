FROM phusion/baseimage:0.10.1

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# Dependencies
RUN	apt-get -y update && \
	apt-get -y install python-pip gdebi-core python3-dev python3-pip python-dev libtool-bin wget emacs iputils-ping

# AWS
RUN	pip3 install awscli boto3
RUN	mkdir /root/AWS
ADD	AWS /root/AWS

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
