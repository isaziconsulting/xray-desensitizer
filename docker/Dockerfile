# Use phusion/baseimage as base image. To make your builds
# reproducible, make sure you lock down to a specific version, not
# to `latest`! See
# https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
# for a list of version numbers.
FROM isazi/xray-desensitizer

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# environment variables
ENV datapath /host
ENV writepath /host/Desktop

# ...put your own build instructions here...
# Update aptitude with new repo
RUN apt-get update
# Install software
RUN apt-get install -y git
# Clone the conf files into the docker container
CMD git clone https://github.com/isaziconsulting/xray-desensitizer.git && cd xray-desensitizer/src && python3 clean_xrays.py --inpath=${datapath} --outpath=${writepath}

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
