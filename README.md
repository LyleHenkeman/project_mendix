# project_mendix


# Part 1

You are given a directory with hundreds of files. Each file contains a sorted list of hundreds of words, one word per line. Using a programming language that you are comfortable with, your task is to come up with an efficient and scalable solution that merges the content of all the files into one sorted file.

 

Attached you can find two archive files with some example test data, a small example with 5 files and a medium sized one with 500 files.

 

 

# Part 2

Create a REST API to expose the aforementioned service and deploy this service in AWS. You’re free in your choice, e.g. EC2 instance, Beanstalk, …

 

# (Bonus)
Secure the API setting up an SSL, so the service supports https.



 

# Part 3

Create a Mendix app which consumes the api and enables the user to upload the files, input of the algorithm, plus returns the output of the service, the resulting file.

We want from him to come up with an automated test for the api. No guidance here, free choice.


# Running
	Install Python
	Install virtualenv
	source the virtualenv	
	```
	pip install -r requirements.txt
	python sorter.py [FOLDER TO INPUT DATA] -o [OUTPUT FILENAME] -d [DO NOT REMOVE DUPLCIATES]
	```

# Notes
	This has only been tested on Linux using Python 2.7
