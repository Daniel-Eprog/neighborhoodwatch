#### WELCOME TO NEIGHBORHOOD WATCH - A CRIME DATABASE APPLICATION ####

#### 1. PREREQUISITES ####

You're going to need a couple of prerequisites before you get started working on the app.
1) Download the latest version of Python - https://www.python.org/downloads/
2) Install pip - Most python environments will come preinstalled with pip but if yours is not you can run the following commands in your CLI
        - python3 -m ensurepip --upgrade
        - python3 get-pip.py
3) Install Django - After you've installed pip it should be easy to have django installed. Just run the following command
        - python3 -m pip install Django
4) Finally install the oracledb python module to access the CISE database - https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html

#### 2. GETTING STARTED ####

If you're unfamiliar with Django I definitely recommend going through the tutorial real quick for any answers you might need. If you follow it step by step 
you'll get the necessary essentials within an hour or two. 

####IMPORTANT NOTE####
The tutorial will cover using a database native with Django. However for the implementation, since i am working on apple silicon which runs
on ARM I cannot use the necessary cx_oracle module or the oracle instant client since they run on x86. But do not fret if you're in the same boat or 
thinking about manually integrating a database stresses you out its not too difficult.

Remember to fork your own repository before getting started and work on your own branch before making any merges.**

Once, you've forked and cloned your repository in the directory of your choice you have to manually connect to your data base since its currently hard 
coded to go to mine.

To do this navigate into the directory "/neighborhoodwatch/neighborhoodwatch/querydata/views.py" 
Once in this file look within the function oracle.connect() and change where is says user esteban.medero and change it to your user credentials.

Now its time to run the app. In your CLI navigate to the first directory neighborhood watch containing the manage.py file and type the following command:

        -python3 manage.py runserver
        
You will be prompted for a password. This is your autogenerated CISE DB password found here https://register.cise.ufl.edu/oracle/

The only page currently set up is the query page since Its going to take the most time to complete I decided to start there. You can now access the 
database at http://127.0.0.1:8000/querydata/ in your webbrowser.

#### DEMO PHOTOS ####

<img width="1511" alt="Screenshot 2023-04-24 at 6 28 01 PM" src="https://user-images.githubusercontent.com/39196999/234130064-dba5f938-80b2-46c1-ae62-44e8671da2b2.png">

<img width="1510" alt="Screenshot 2023-04-24 at 6 28 24 PM" src="https://user-images.githubusercontent.com/39196999/234130128-4a0b541c-e0b1-41c5-83f6-dcb4cbb47d07.png">

<img width="1510" alt="Screenshot 2023-04-24 at 6 29 31 PM" src="https://user-images.githubusercontent.com/39196999/234130271-20b6d9a1-5707-4fd7-a9cf-b7efc2da7be8.png">

<img width="1182" alt="Screenshot 2023-04-24 at 6 32 53 PM" src="https://user-images.githubusercontent.com/39196999/234130707-068857f5-dd18-4357-8ee9-a7d37a445fa3.png">

<img width="1182" alt="Screenshot 2023-04-24 at 6 36 35 PM" src="https://user-images.githubusercontent.com/39196999/234131176-b9d315b0-f9b8-4640-b3df-4a5f76a57778.png">


