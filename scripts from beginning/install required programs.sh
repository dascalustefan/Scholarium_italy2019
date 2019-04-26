#!/bin/bash
cd /tmp
wget https://www.multichain.com/download/multichain-2.0.1.tar.gz
tar -xvzf multichain-2.0.1.tar.gz
cd multichain-2.0.1
mv multichaind multichain-cli multichain-util /usr/local/bin

pip3 install Flask
pip3 install SQLAlchemy
pip3 install flask-sqlalchemy
pip3 install flask-marshmallow

apt install mysql-server libmysqlclient-dev

mysql -e "CREATE DATABASE scholarium_db"
mysql -e "CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"
mysql -e "CREATE TABLE IF NOT EXISTS scholarium_db.university (
	    id INT AUTO_INCREMENT PRIMARY KEY,
	    name VARCHAR(255) NOT NULL,
	    pubkey VARCHAR(255) NOT NULL,
	    address VARCHAR(255) NOT NULL);"
mysql -e "CREATE TABLE IF NOT EXISTS scholarium_db.student (
	    cnp VARCHAR(25) PRIMARY KEY,
	    name VARCHAR(255) NOT NULL,
	    pubkey VARCHAR(255) NOT NULL,
	    address VARCHAR(255) NOT NULL,
	    multisig VARCHAR(255) NOT NULL);"
mysql -e "CREATE TABLE IF NOT EXISTS scholarium_db.diploma (
	    hash VARCHAR(255) PRIMARY KEY,
	    student_cnp VARCHAR(25),
	    name VARCHAR(255) NOT NULL,
	    CONSTRAINT fk_diploma_student
	    FOREIGN KEY (student_cnp)
  	    REFERENCES scholarium_db.student (cnp)
            ON DELETE CASCADE);"
	    
pip3 install mysqlclient