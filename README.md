

# Team1
Web application to compare music tastes!

# Instructions to Run (Windows)
1. Open cmd prompt, navigate to the project directory. (example below)

		cd  C:\Users\Username\Documents\ProjectName
2. Create Virtual Environment for python.

		python3 -m venv /venv/
3. Install required packages:

		pip install -r requirements.txt

4. Create file called flask.ini in the Config folder.

5. Add the following to the flask.ini file (note your_secret_key should be a random key you generate):  

		[flask]  
		secret_key=YOUR_SECRET_KEY
		
6. Create file called sql.ini in the Config folder.

7. Add the following to the sql.ini file (change the placeholders to your database connection):

		[sql]
		user=USERNAME
		password=PASSWORD
		host=ADDRESS
		database=DBNAME

8. Start the app with run.py

		python3 run.py

9. If everything is done correctly the console will give you the localhost address. Clicking that address takes you to the website.
