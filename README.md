# MoniCrop Hardware

A crop monitoring system made using a Raspberry Pi 4B, a 7-in-1 NPK sensor, an ultrasonic sensor, and an ESP32 Wi-Fi module.

## Features

- **Real-time Soil Monitoring**: pH, moisture, temperature, conductivity, nitrogen, phosphorus, potassium (NPK)
- **Plant Growth Tracking**: Ultrasonic distance sensor for growth rate calculation
- **WiFi Connectivity**: ESP32 module provides WiFi access to Raspberry Pi
- **Cloud Integration**: Data stored in Firebase Firestore
- **Telegram Notifications**: Real-time alerts and data reports
- **Automated Scheduling**: Data collection at configurable intervals (8-10 AM, 12-2 PM, 8-10 PM)

## Hardware Components

- Raspberry Pi 4B
- 7-in-1 NPK Soil Sensor (RS485)
- HC-SR04 Ultrasonic Distance Sensor
- ESP32 WiFi Module
- USB to RS485 Converter

## Setup Instructions

### 1. Raspberry Pi Setup

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install python-dotenv RPi.GPIO pyserial geocoder requests firebase-admin pyTelegramBotAPI telethon google-cloud-firestore
```

#### Configure Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your actual configuration:
   - Firebase credentials and API key
   - Telegram API credentials
   - Serial port settings
   - Location and plant IDs

#### Raspberry Pi Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase service account key | `/path/to/serviceAccountKey.json` |
| `FIREBASE_API_KEY` | Firebase API key | `AIza...` |
| `FIREBASE_EMAIL` | Firebase auth email | `user@example.com` |
| `FIREBASE_PASSWORD` | Firebase auth password | `your_password` |
| `TELEGRAM_API_ID` | Telegram API ID | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API hash | `abcd1234...` |
| `TELEGRAM_PHONE` | Telegram phone number | `+1234567890` |
| `TELEGRAM_USERNAME` | Telegram username | `yourusername` |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel ID | `@yourchannel` |
| `LOCATION_ID` | Location identifier | `ABC123` |
| `PLANT_ID` | Plant identifier | `XYZ789` |
| `FRUIT_TYPE` | Type of fruit/crop | `mango` |
| `SERIAL_PORT` | Serial port for NPK sensor | `/dev/ttyUSB1` |
| `SERIAL_BAUDRATE` | Serial baudrate | `4600` |

### 2. ESP32 Setup

#### Configure WiFi Credentials

1. Navigate to the wififile directory:

   ```bash
   cd wififile
   ```

2. Copy the config template:

   ```bash
   cp config.h.example config.h
   ```

3. Edit `config.h` and add your WiFi credentials:

   ```cpp
   const char* WIFI_SSID = "your_wifi_ssid";
   const char* WIFI_PASSWORD = "your_wifi_password";
   ```

#### Upload to ESP32

1. Open `wififile.ino` in Arduino IDE
2. Select your ESP32 board (Tools → Board → ESP32 Dev Module)
3. Select the correct port (Tools → Port)
4. Upload the sketch

#### ESP32 Serial Commands

The ESP32 accepts the following commands from Raspberry Pi over serial:

| Command | Description |
|---------|-------------|
| `CONNECT` | Connect to configured WiFi network |
| `DISCONNECT` | Disconnect from WiFi |
| `STATUS` | Get connection status, SSID, signal strength, IP |
| `IP` | Get current IP address |
| `SCAN` | Scan for available WiFi networks |

### 3. Running the System

On the Raspberry Pi:

```bash
python CMPEProject.py
```

The system will:

- Connect to Firebase and authenticate
- Monitor soil conditions every 24 minutes (5 readings per collection window)
- Calculate and send average readings to Firestore
- Send notifications via Telegram
- Track plant growth rate using ultrasonic sensor

**Security Note**: Never commit `.env`, `config.h`, or `serviceAccountKey.json` to version control.

## Hardware Design

![CMPE 495B_bbzzz](https://github.com/emansarahafi/MoniCropHardware/assets/85173630/c912d8f2-5338-4dc2-ae86-52b7e9e9ef4d)

## UML Activity Diagram

![Untitled Diagram drawio](https://github.com/emansarahafi/MoniCropHardware/assets/85173630/ae4a8b18-c2ae-47f9-b5e1-fcfe99bc3c9b)

## Related Projects

This website is part of the **MoniCrop Smart Crop Monitoring System**:

- **[MoniCrop Website](https://github.com/emansarahafi/MoniCropWebsite)** - Functional Website
- **[MoniCrop iOS App](https://github.com/emansarahafi/MoniCropiOS)** - Mobile application for iOS

## Citation

If you use this work, please cite:

```bibtex
@article{Afi2023,
  author = "Eman Sarah Afi",
  title = "{Development of a Smart Crop Monitoring System}",
  year = "2023",
  month = "10",
  url = "https://aubh.figshare.com/articles/thesis/_b_Development_of_a_Smart_Crop_Monitoring_System_b_/30580751",
  doi = "10.58014/aubh.24314056.v2"
}
```

**Published thesis**: [Development of a Smart Crop Monitoring System](https://aubh.figshare.com/articles/thesis/_b_Development_of_a_Smart_Crop_Monitoring_System_b_/30580751) (DOI: 10.58014/aubh.24314056.v2)
