FROM docker.tech.beegroup-cimne.com/admin/enma-job:latest as cached
ENV DEBIAN_FRONTEND=noninteractive
RUN git clone https://github.com/BeeGroup-cimne/beegroup_importing_tool.git
WORKDIR beegroup_importing_tool
RUN pip install -r requirements.txt

FROM cached
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git pull

