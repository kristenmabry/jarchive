import mysql.connector
from password import password

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd=password,
	database="JArchive",
	auth_plugin='mysql_native_password'
)

print(mydb)
mycursor = mydb.cursor()

mycursor.execute("SELECt Id FROM Games Order By Id DESC")

myresult = mycursor.fetchone()

print(myresult[0])
