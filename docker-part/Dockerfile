FROM ubuntu:18.04
WORKDIR /app
COPY . /app
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y libmysqlclient-dev\
 && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip\
 && sed -i "s/127.0.0.1/0.0.0.0/g" /etc/mysql/mysql.conf.d/mysqld.cnf \
 && mkdir /var/run/mysqld \
 && chown -R mysql:mysql /var/run/mysqld
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
RUN mv multichaind multichain-cli multichain-util /usr/local/bin
RUN mkdir -p ~/.multichain
#RUN ./dependenicies1.sh

VOLUME ["/var/lib/mysql"]
 
EXPOSE 80
#CMD ['./dependenicies1.sh']
#CMD ["python3", "main.py"]

