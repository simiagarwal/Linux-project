
Linux-project

Description:

This project is to deploy a Flask application using Ubuntu and Apache with Amazon Lightsail.

IP & Hostname

Host Name: ec2-54-191-206-214.us-west-2.compute.amazonaws.com

IP Address: 54.191.206.214

Linux Configuration


 Create a user called grader. 
 $ sudo adduser grader. 
create a file to give the user grader superuser privileges.  
$ sudo nano /etc/sudoers.d/grader. T. 
When nano opens type grader ALL=(ALL:ALL)

Updating package list, upgrading the current packages, and install new updates with these three commands:

$ sudo apt-get update

$ sudo apt-get upgrade

$ sudo apt-get dist-upgrade

 install  Finger with the command:
 sudo apt-get install finger. This tool will allow us to see the users on this server.

Now we must create an SSH Key for our new user grader. 
 $ ssh-keygen -f ~/.ssh/udacity.rsa

 Copy the public key using the command: 
 $ cat ~/.ssh/udacity.rsa.pub. Copy the key from the terminal.

Back in the server terminal  
$ cd /home/grader to move to the folder.

Create a directory called .ssh with the command 
$ mkdir .ssh

Create a file to store the public key with the command 
$ touch .ssh/authorized_keys

Edit that file using 
$ nano .ssh/authorized_keys

Now paste in the public key

We must change the permissions of the file and its folder by running

$ sudo chmod 700 /home/grader/.ssh

$ sudo chmod 644 /home/grader/.ssh/authorized_keys 

Change the owner of the .ssh directory from root to grader by using the command 
$ sudo chown -R grader:grader /home/grader/.ssh

The last thing we need to do for the SSH configuration is restart its service with 
$ sudo service ssh restart
Disconnect from the server

Now we need to login with the grader account using ssh. From your local terminal type 
$ ssh -i ~/.ssh/udacity.rsa grader@54.191.206.214

Configure the firewall using these commands:
$ sudo ufw allow 2200/tcp
$ sudo ufw allow 80/tcp
$ sudo ufw allow 123/udp
$ sudo ufw enable

Running $ sudo ufw status should show all of the allowed ports with the firewall configuration.

Application Deployment

Hosting this application will require the Python virtual environment, Apache with mod_wsgi, PostgreSQL, and Git.

Start by installing the required software

$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi python-dev
$ sudo apt-get install git

Enable mod_wsgi with the command $ sudo a2enmod wsgi and restart Apache using $ sudo service apache2 restart.

Create a directory for our catalog application and make the user grader the owner.

$ cd /var/www

$ sudo mkdir catalog

$ sudo chown -R grader:grader catalog

$ cd catalog

In this directory we will have our catalog.wsgi file var/www/catalog/catalog.wsgi, our virtual environment directory which we will create soon and call venv /var/www/catalog/venv, and also our application which will sit inside of another directory called catalog /var/www/catalog/catalog.
clone our Catalog Application repository by $ git clone [https://github.com/simiagarwal/Catalog-Final.git] catalog
Create the .wsgi file by $ sudo nano catalog.wsgi and make sure your secret key matches with your project secret key
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/catalog/")

from catalog import app as application
application.secret_key = 'super_secret_key'
Rename your application.py, project.py, or whatever you called it in your catalog application folder to __init__.py by $ mv project.py __init__.py
Now lets create our virtual environment, make sure you are in /var/www/catalog.
$ sudo pip install virtualenv
$ sudo virtualenv venv
$ source venv/bin/activate
$ sudo chmod -R 777 venv
While our virtual environment is activated we need to install all packages required for our Flask application. Here are some defaults but you may have more to install.
$ sudo apt-get install python-pip
$ sudo pip install flask
$ sudo pip install httplib2 oauth2client sqlalchemy psycopg2 #etc...
Time to configure and enable our virtual host to run the site

$ sudo nano /etc/apache2/sites-available/catalog.conf
Paste in the following:

<VirtualHost *:80>
    ServerName 54.191.206.214
    ServerAlias ec2-54-191-206-214.us-west-2.compute.amazonaws.com
    ServerAdmin admin@54.191.206.214
    WSGIDaemonProcess catalog python-path=/var/www/catalog:/var/www/catalog/venv/lib/python2.7/site-packages
    WSGIProcessGroup catalog
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>


Enable to virtual host: $ sudo a2ensite catalog.conf 
DISABLE the default host $ a2dissite 000-default.conf 

The final step is setting up the database

$ sudo apt-get install libpq-dev python-dev
$ sudo apt-get install postgresql postgresql-contrib
$ sudo su - postgres -i
$ psql
Create a database user and password
postgres=# CREATE USER catalog WITH PASSWORD [password];
postgres=# ALTER USER catalog CREATEDB;
postgres=# CREATE DATABASE catalog with OWNER catalog;
postgres=# \c catalog
catalog=# REVOKE ALL ON SCHEMA public FROM public;
catalog=# GRANT ALL ON SCHEMA public TO catalog;
catalog=# \q
$ exit


Now use nano again to edit your__init__.py, database_setup.py, and createitems.py files to change the database engine from sqlite://catalog.db to postgresql://username:password@localhost/catalog enter image description here

Restart your apache server $ sudo service apache2 restart and now your IP address and hostname should both load your application.

References:
https://github.com/callforsky/udacity-linux-configuration

