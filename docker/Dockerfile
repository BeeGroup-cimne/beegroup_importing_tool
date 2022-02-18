FROM docker.tech.beegroup-cimne.com/admin/enma-job:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN git clone https://github.com/BeeGroup-cimne/beegroup_importing_tool.git
WORKDIR beegroup_importing_tool
RUN git pull
RUN pip install -r requirements.txt
