# scholarium

To install the necessary dependecies, run the dependencies.sh script from the commands directory, using bash.

To create a new multichain, run the create_multichain.py script from the commands directory, using python3.

To clean the database, run clean.sh script from the commands directory, using bash.It only cleans the tables but does not actually delete the database

This project is made as a result of a paper titled Scholarium. Which we have included in this paper and will be updated regularly from now on according to new additions .

To run the dockers first build one with the command : sudo docker build --tag=test1 . while in the docker-part folder.
After the setup finishes you run each docker with the command:
sudo docker run -p 5000:80 -it test1 with 5000 being the port you want to connect to the program to.
after you have ran the machine you need to start the mysql server so run this command:  /etc/init.d/mysql start
after which run ./dependenicies1.sh
and to start the program: python3 main.py.
From the main machine you can connect with 127.0.0.1:5000 or whatever port you chose .

For any unknown stuff email st3fandascalu@gmail.com or avram.andreimarius@gmail.com

