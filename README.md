
Linux-project
2
Description:
3
This project is to deploy a Flask application using Ubuntu and Apache with Amazon Lightsail.
4
​
5
IP & Hostname
6
Host Name: ec2-54-191-206-214.us-west-2.compute.amazonaws.com
7
IP Address: 54.191.206.214
8
Linux Configuration
9
​
10
On Mac you will want to store all of your SSH Keys in the .ssh folder which is located in a folder called .ssh at the root of your user directory. For example Macintosh HD/Users/[Your username]/.ssh/
11
​
12
To make our key secure type $ chmod 600 ~/.ssh/udacity.pem into the terminal.
13
From here we will log into the server as the user ubuntu with our key. From the terminal type $ ssh -i ~/.ssh/udacity.pem ubuntu@18.188.169.39
14
Once logged in you will see the command line change to root@[ip-your-private-ip]:$
15
Lets switch to the root user by typing sudo su -
16
As Udacity requires we need to create a user called grader. From the command line type $ sudo adduser grader. It will ask for 2 passwords and then a few other fields which you can leave blank.
17
We must create a file to give the user grader superuser privileges. To do this type $ sudo nano /etc/sudoers.d/grader. This will create a new file that will be the superuser configuration for grader. When nano opens type grader ALL=(ALL:ALL), to save the file hit Ctrl-X on your keyboard, type 'Y' to save, and return to save the filename.
18
One of the first things you should always do when configuring a Linux server is updating it's package list, upgrading the current packages, and install new updates with these three commands:
19
$ sudo apt-get update
20
$ sudo apt-get upgrade
21
$ sudo apt-get dist-upgrade
22
​
23
We will also install a useful tool called Finger with the command $ sudo apt-get install finger. This tool will allow us to see the users on this server.
24
Now we must create an SSH Key for our new user grader. From a new terminal run the command: $ ssh-keygen -f ~/.ssh/udacity.rsa
25
In the same terminal we need to read and copy the public key using the command: $ cat ~/.ssh/udacity.rsa.pub. Copy the key from the terminal.
26
Back in the server terminal locate the folder for the user grader, it should be /home/grader. Run the command $ cd /home/grader to move to the folder.
27
Create a directory called .ssh with the command $ mkdir .ssh
28
Create a file to store the public key with the command $ touch .ssh/authorized_keys
29
Edit that file using $ nano .ssh/authorized_keys
30
Now paste in the public key
31
We must change the permissions of the file and its folder by running
32
$ sudo chmod 700 /home/grader/.ssh
33
$ sudo chmod 644 /home/grader/.ssh/authorized_keys 
34
Change the owner of the .ssh directory from root to grader by using the command $ sudo chown -R grader:grader /home/grader/.ssh
35
The last thing we need to do for the SSH configuration is restart its service with $ sudo service ssh restart
36
Disconnect from the server
37
Now we need to login with the grader account using ssh. From your local terminal type $ ssh -i ~/.ssh/udacity.rsa grader@18.188.169.39
38
You should now be logged into your server via SSH
39
Lets enforce key authentication from the ssh configuration file by editing $ sudo nano /etc/ssh/sshd_config. Find the line that says PasswordAuthentication and change it to no. Also find the line that says Port 22 and change it to Port 2200. Lastly change PermitRootLogin to no.
40
Restart ssh again: $ sudo service ssh restart
41
Disconnect from the server and try step "23." again BUT also adding -p 2200 at the end this time. You should be connected.
42
From here we need to configure the firewall using these commands:
43
$ sudo ufw allow 2200/tcp
44
$ sudo ufw allow 80/tcp
45
$ sudo ufw allow 123/udp
46
$ sudo ufw enable
47
Running $ sudo ufw status should show all of the allowed ports with the firewall configuration.
48
That pretty much wraps up the Linux configuration, now onto the app deployment.
49
Application Deployment
50
Hosting this application will require the Python virtual environment, Apache with mod_wsgi, PostgreSQL, and Git.
51
​
52
Start by installing the required software
53
$ sudo apt-get install apache2
54
$ sudo apt-get install libapache2-mod-wsgi python-dev
55
$ sudo apt-get install git
56
Enable mod_wsgi with the command $ sudo a2enmod wsgi and restart Apache using $ sudo service apache2 restart.
57
If you input the servers IP address into a web browser you'll see the Apache2 Ubuntu Default Page
58
We now have to create a directory for our catalog application and make the user grader the owner.
59
$ cd /var/www
60
$ sudo mkdir catalog
61
$ sudo chown -R grader:grader catalog
62
$ cd catalog
63
In this directory we will have our catalog.wsgi file var/www/catalog/catalog.wsgi, our virtual environment directory which we will create soon and call venv /var/www/catalog/venv, and also our application which will sit inside of another directory called catalog /var/www/catalog/catalog.
