
Steps to run this project :

Go to your vagrant environment and ssh into the virtual machine by using the following commands :

$ vagrant up
$ vagrant ssh
Once you have logged into your VM, use the follow command to enter the directory containing the project :

$ cd /vagrant/catalog
Once your in the directory run the following commands to initialise and populate the Database :

$ python database_setup.python
$ python catalogwithusers.py

Once you have run the above commands successfully, you should see a catalogwithusers.db named file in your local directory /catalog

Run the following command to run the app :

$ python project.py
