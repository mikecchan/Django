<h1> Udacity Full Stack Nanodegree Project 4 "Items Catalog Project" </h1>

In my fourth project, I built a simple basic online store where a user can view
	inventory of sporting goods.  The user can then login and make changes to the
	inventory by creating, updating, and deleting items.
	

The points of this project is to demonstrate my main understanding of...

	1.	Django Framework
	
	2.	CRUD (Create, Read, Update, and Delete data)
	
	3.	Authorization and Authentication


<h3>Instruction to run my project...</h3>

	1. 	My project will be ran in a virtual machine.  So if you have not already,
		download VirtualBox (https://www.virtualbox.org/wiki/Downloads)
		
		VirtualBox is the software that actually runs the virtual machine (VirtualBox in 
		this instance)
		
	2.	Next you would download Vagrant (https://www.vagrantup.com/downloads.html).
		Vagrant is the software that configures the Virtual Machine to let you share 
		files between your host computer and VirtualBox.
		
	3.	Download my Project and put in a location of your choice on the PC.
		
	
	4.	Go to your terminal and perform the following...
	
		i.		navigate and cd to the 'Vagrant' folder
			
		ii.		run 'Vagrant up'
		
		iii.	run 'Vagrant ssh'
		
		iv.		run 'cd /Vagrant/vagrant/catalog'
		
		v.		run 'ls' to ensure you see my project files (application.py, setup_db.py, 
				etc.)
		
		vi.		run 'python setup_db.py' to create the database where sports inventory
				will be stored.
		
		vii.	run 'python add_items.py' to add items to tables in the database that
				you just created.
				
		viii.	run 'python application.py' to run the project on a localhost in
				virtual machine.
				
		xiv.	Open your browser and go to 'http://localhost:8000'.
		
		xv.		Enjoy!
		
		xvi.	If you would like to login to Create, Read, and Update items on my project,
				After you click on the google login link...
				My gmail user is 'mchanudacity@gmail.com'
				The password is 'mchanudacity1'
				(Please don't mess with the gmail account, this is my account to be used
				for the public for this project only).
		
	5.	And you're done!  If you have come to an error somewhere along following the
		instructions, then please view the attached PDF: "Items_Catalog_Project.pdf" to
		view how it would look like.