FROM jenkins/jenkins:lts

ARG DOCKER_GID

USER root
RUN apt-get update && \
    apt-get install -y lsb-release apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
    apt-get clean
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc https://download.docker.com/linux/debian/gpg
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean
RUN curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
RUN groupmod -g ${DOCKER_GID} docker
RUN usermod -aG docker jenkins

USER jenkins
