
'''

	SERVER CODE FOR THE REDUCTION OF DRUNK AND DRIVE CASES

'''

import MySQLdb

import ast
import paho.mqtt.client as mqtt
import time
import json
import datetime
from datetime import timedelta
import uuid

# twilio module
from twilio.rest import TwilioRestClient

# message = ast.literal_eval(data)

'''
	create database projectspace;

	create table driverData (car_no varchar(10) PRIMARY KEY,name varchar(50),age int, license_no varchar(50),blockstatus boolean, blockcode varchar(6));

	INSERT INTO driverData(car_no,name,age,license_no,blockstatus,blockcode) VALUES ('AP95AH4','Rajeev',26,'apdofi234',false);

'''

def sql_Connection(sql_hostName,user,password,Database):
	global cursor,db
	
	# Open database connection
	db = MySQLdb.connect(sql_hostName,user,password,Database)

	# prepare a cursor object using cursor() method
	cursor = db.cursor()	

def on_connect(client, userdata, flags, rc):
	print "Connected with result code "+str(rc)
	(result,mid)= client.subscribe(SUB_TOPIC)
	print result

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))

	if (msg.topic == "alcohol"):

		driver_Data = {}

		data = msg.payload

		Car_no = str(msg.payload).split(",")[1] # get the number from the message


		sql = "SELECT * FROM "+tableName+" WHERE car_no =""'"+Car_no+"'"""
		print sql

		# Execute the SQL command
		cursor.execute(sql)

		# Fetch all the rows in a list of lists.
		results = cursor.fetchall()

		if len(results) > 0:
			for row in results:
				driver_Data.update({row[0]:{"car_no":row[0],"name":row[1],"license_no":row[3],"blockstatus":row[4],"blccktime":row[5]}})

			if (row[4] == 0):	
			

				# block code generation
				driver_Data[Car_no].update({"blockcode":str(uuid.uuid4())[:4]})



				# block code and status update in database
				sql = "UPDATE "+tableName+" SET blockcode = ""'"+str(driver_Data[Car_no]["blockcode"])+"'"",blockstatus = true WHERE car_no = ""'"+Car_no+"'"""
				print sql
				
				# Execute the SQL command
				cursor.execute(sql)
				# Commit your changes in the database
				db.commit()


				# # sending twilio message to relatives
				print driver_Data
				
				# sending twilio message to police 

				police_data = {"1234":{"name":"Mark","area":"Nevada","phone_no":"+919550119531"}}

				police_messageBody = "Mr."+driver_Data[Car_no]["name"]+" with license_no "+driver_Data[Car_no]["car_no"]+" consumed more alcohol, Block code - "+driver_Data[Car_no]["blockcode"]+""

				print police_messageBody
				print "\n\n\tMessage Sent"
				# twilioClient.messages.create(body=police_messageBody,to=police_data["1234"]["phone_no"],from_=twilionumber)

	if (msg.topic == "police"):

		driver_Data_unblock = {}

		carNo = msg.payload.split(",")[0]
		code  = msg.payload.split(",")[1]

		if (msg.payload["id"] in police_data.keys()):

			sql = "SELECT * FROM "+tableName+" WHERE car_no =""'"+carNo+"'"""
			print sql

			# Execute the SQL command
			cursor.execute(sql)

			# Fetch all the rows in a list of lists.
			results = cursor.fetchall()

			if len(results) > 0:
				for row in results:
					if (row[0] == carNo):
						driver_Data_unblock.update({"car_no":row[0],"name":row[1],"license_no":row[3],"blockstatus":row[4],"blockcode":row[5]})
			
			if driver_Data_unblock["blockcode"] == code:
				# block code and status update in database
				sql = "UPDATE "+tableName+" SET blockcode = null,blockstatus = false WHERE car_no = ""'"+Car_no+"'"""
				print sql
				
				# Execute the SQL command
				cursor.execute(sql)
				# Commit your changes in the database
				db.commit()






def mqtt_Send(message,channel):
	(result,mid) = mqttc.publish(channel,message,2)
	print result
	# pass


def mqtt_Connection(mqtt_hostName,mqtt_portnumber,timealive):
	global mqttc
	mqttc = mqtt.Client()
	mqttc.on_connect = on_connect
	mqttc.on_message = on_message

	mqttc.connect(mqtt_hostName,mqtt_portnumber,timealive)


	mqttc.loop_start()
	mqttc.loop_forever()
	

if __name__ == '__main__':

	Database = "projectspace"
	tableName = "driverData"
	sql_hostName = 'localhost'
	user = 'root'
	password = 'rbed1421'

	mqtt_hostName = '34.226.134.195'
	mqtt_portnumber = 1883
	timealive = 60

	police_data = {"1234":{"name":"Mark","area":"Nevada","phone_no":"+919550119531"}}
	SUB_TOPIC = "alcohol"


	account_sid = "ACcb5986f222c5ab6dddf2ca80af818ef2" # Enter your account sid 
	auth_token  = "1a2f64a2df18ab8a59e7b11d457be2a7"   # Enter your auth token


	twilioClient = TwilioRestClient(account_sid, auth_token)

	twilionumber = "+14798887804" # Your Twilio phone Number you will get it while registration
	receivernumber = "+919550119531" #Your verified phone number

	

	sql_Connection(sql_hostName,user,password,Database)
	mqtt_Connection(mqtt_hostName,mqtt_portnumber,timealive)	
	

