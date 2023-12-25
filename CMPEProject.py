import RPi.GPIO as GPIO
import serial
import datetime
import time
import geocoder
import os
import requests
import json
import firebase_admin
import telebot
import configparser
import asyncio
from telethon.sync import TelegramClient  
from telethon.tl.types import InputPeerUser, InputPeerChannel  
from telethon import TelegramClient, sync, events
from google.cloud import firestore
from firebase_admin import credentials, auth

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up ultrasonic sensor
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialize the geocoder
g = geocoder.ip('me')

# Initialize Firestore client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/emanpi/Desktop/serviceAccountKey.json"
db = firestore.Client()

# Fetch the service account key JSON file path
cred = credentials.Certificate("/home/emanpi/Desktop/serviceAccountKey.json")

# Initialize the app
firebase_admin.initialize_app(cred)

# Set the API endpoint
auth_url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=INSERT_API_KEY_HERE'

# Set the request body
data = {
    "email": "john.doe@example.com",
    "password": "123",
    "returnSecureToken": True
}

# Send the POST request to the API endpoint
response = requests.post(auth_url, data=json.dumps(data))

# Create function to extract data from Telegram channel
def telegram(notification):
   # Reading Configs
   config = configparser.ConfigParser()
   config.read("/home/emanpi/Desktop/config.ini")

   # Setting configuration values
   api_id = config['Telegram']['api_id']
   api_hash = config['Telegram']['api_hash']

   api_hash = str(api_hash)

   phone = config['Telegram']['phone']
   username = config['Telegram']['username']

   # Create the client and connect
   client = TelegramClient(username, api_id, api_hash)

   async def main(phone):
       await client.start()
       print("Client Created")
       me = await client.get_me()

       my_channel = await client.get_entity('INSERT_CHAT_ID_HERE')
       messages = await client.send_message('INSERT_CHAT_ID_HERE', message=notification)

   with client:
       client.loop.run_until_complete(main(phone))

# NPK sensor being set up
uart0 = serial.Serial(port='/dev/ttyUSB1', baudrate=4600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

temp = bytes.fromhex('01 03 00 13 00 01 75 cf')
moist = bytes.fromhex('01 03 00 12 00 01 24 0F')
econ = bytes.fromhex('01 03 00 15 00 01 95 ce')
ph = bytes.fromhex('01 03 00 06 00 01 64 0b')
nitro = bytes.fromhex('01 03 00 1e 00 01 e4 0c')
phos = bytes.fromhex('01 03 00 1f 00 01 b5 cc')
pota = bytes.fromhex('01 03 00 20 00 01 85 c0')   

def read_ultrasonic():
    GPIO.output(TRIG, False)
    time.sleep(2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def temperature():
    if uart0.write(temp):
        Rx_Temp = uart0.read(7)
        print("Received data : " + str(Rx_Temp))
        Temperature_Value = int.from_bytes(Rx_Temp[3:5], 'big')
        return Temperature_Value
    else:
        print("Data Didn't Transmit")

def moisture():
    if uart0.write(moist):
        Rx_Moisture = uart0.read(7)
        print("Received data : " + str(Rx_Moisture))
        Moisture_Value = int.from_bytes(Rx_Moisture[3:5], 'big')
        return Moisture_Value
    else:
        print("Data Didn't Transmit")

def conductivity():
    if uart0.write(econ):
        Rx_Econ = uart0.read(7)
        print("Received data : " + str(Rx_Econ))
        Conductivity_Value = int.from_bytes(Rx_Econ[3:5], 'big')
        return Conductivity_Value
    else:
        print("Data Didn't Transmit")

def phv():
    if uart0.write(ph):
        Rx_Ph = uart0.read(7)
        print("Received data : " + str(Rx_Ph))
        Ph_Value = int.from_bytes(Rx_Ph[3:5], 'big')
        return Ph_Value
    else:
        print("Data Didn't Transmit")

def nitrogen():
    if uart0.write(nitro):
        Rx_Nitro = uart0.read(7)
        print("Received data : " + str(Rx_Nitro))
        Nitrogen_Value = int.from_bytes(Rx_Nitro[3:5], 'big')
        return Nitrogen_Value
    else:
        print("Data Didn't Transmit")

def phosphorus():
    if uart0.write(phos):
        Rx_Phos = uart0.read(7)
        print("Received data : " + str(Rx_Phos))
        Phosphorus_Value = int.from_bytes(Rx_Phos[3:5], 'big')
        return Phosphorus_Value
    else:
        print("Data Didn't Transmit")

def potassium():
    if uart0.write(pota):
        Rx_Pota = uart0.read(7)
        print("Received data : " + str(Rx_Pota))
        Potassium_Value = int.from_bytes(Rx_Pota[3:5], 'big')
        return Potassium_Value
    else:
        print("Data Didn't Transmit")

# Define the ID for the location and the plant
location_id = "ABC123"
plant_id = "XYZ789"

# Define a variable to store the previous distance value
prev_D = 0

# Loop to receive data and write to Firestore
while True:
    # Get the current time and location
    now = datetime.datetime.now()

    # Get the city of the current location
    city = g.city

    # Check if the request was successful
    if response.status_code == 200:
        # Get the ID token from the response
        id_token = response.json()['idToken']

        # Decode the token to retrieve the user ID
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']

        # Print the user ID
        print("User ID:", user_id)
    else:
        # If the request failed, print the error message
        print(response.json()['error']['message'])
   
    # Check if the current time is within any of the specified time ranges
    if (now.hour >= 8 and now.hour < 10) or (now.hour >= 12 and now.hour < 14) or (now.hour >= 20 and now.hour < 22):
        # Create lists to store the sensor data
        temperatures = []
        moistures = []
        conductivities = []
        ph_values = []
        nitrogens = []
        phosphoruses = []
        potassiums = []
        distances = []
       
        # Loop to collect data every 24 minutes
        for i in range(5):
            # Receive data
            T = temperature()/100
            M = moisture()/100
            C = conductivity()
            pH = phv()/100
            N = nitrogen()
            P = phosphorus()
            K = potassium()
            D = read_ultrasonic()

            # Print the sensor data
            print("Temperature : " + str(T))
            print("Moisture : " + str(M))
            print("Conductivity : " + str(C))
            print("pH : " + str(pH))
            print("Nitrogen : " + str(N))
            print("Phosphorus : " + str(P))
            print("Potassium : " + str(K))
            print("Distance : " + str(D))

            # Add the sensor data to the lists
            temperatures.append(T)
            moistures.append(M)
            conductivities.append(C)
            ph_values.append(pH)
            nitrogens.append(N)
            phosphoruses.append(P)
            potassiums.append(K)
            distances.append(D)

            # Wait for 24 minutes before collecting more data
            time.sleep(1440)

        # Compute the averages of the sensor data
        avg_T = round(sum(temperatures) / len(temperatures), 2)  # calculate average temperature
        avg_M = round(sum(moistures) / len(moistures), 2)  # calculate average moisture
        avg_C = round(sum(conductivities) / len(conductivities), 2)  # calculate average conductivity
        avg_pH = round(sum(ph_values) / len(ph_values), 2)  # calculate average pH
        avg_N = round(sum(nitrogens) / len(nitrogens), 2)  # calculate average Nitrogen
        avg_P = round(sum(phosphoruses) / len(phosphoruses), 2)  # calculate average Phosphorus
        avg_K = round(sum(potassiums) / len(potassiums), 2)  # calculate average Potassium
        avg_D = round(sum(distances) / len(distances), 2)  # calculate average Distance        

        # Calculate growth rate of the distance
        growth_rate = round((avg_D - prev_D) / avg_D * 100, 2)

        # Update previous distance value
        prev_D = avg_D
        
        # Write sensor data to Firestore
        doc_ref = db.collection(u'soil_data').document()
        doc_ref.set({
            "Timestamp": datetime.datetime.now(),
            "userId": user_id,
            "Location": city,
            "Location ID": location_id,
            "id": plant_id,
            "fruit": "mango",
            "pH": avg_pH,
            "Conductivity": avg_C,
            "Temperature": avg_T,
            "Moisture": avg_M,
            "Nitrogen": avg_N,
            "Phosphorus": avg_P,
            "Potassium": avg_K,
            "Distance": growth_rate
        })
   
        print("Written")
        
        # Send average sensor data to Telegram chat
        notification = f"Timestamp: {now} \nUserID: {user_id} \nLocation: {city} \nLocation ID: {location_id} \nPlant ID: {plant_id} \nGrowth Rate: {growth_rate} %\nAverage temperature: {avg_T} °C\nAverage moisture: {avg_M}%\nAverage conductivity: {avg_C} mS/cm\nAverage pH: {avg_pH}\nAverage nitrogen: {avg_N} ppm\nAverage phosphorus: {avg_P} ppm\nAverage potassium: {avg_K} ppm"
        telegram(notification)
   
    # Wait for some time before checking the time again
    time.sleep(60)
