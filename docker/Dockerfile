FROM docker.tech.beegroup-cimne.com/base_dockers/enma-job-3.10:latest as cached
ENV DEBIAN_FRONTEND=noninteractive
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/BeeGroup-cimne/beegroup_importing_tool.git
WORKDIR beegroup_importing_tool
RUN pip install -r requirements.txt

FROM cached
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git pull

