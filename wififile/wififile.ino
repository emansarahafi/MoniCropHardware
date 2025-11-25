#include <WiFi.h>
#include "config.h"

// WiFi credentials are defined in config.h
// Copy config.h.example to config.h and add your credentials

// Commands from RPi
#define CMD_CONNECT "CONNECT"
#define CMD_DISCONNECT "DISCONNECT"
#define CMD_STATUS "STATUS"
#define CMD_IP "IP"
#define CMD_SCAN "SCAN"

String inputString = "";
bool stringComplete = false;

void setup() {
  // Initialize the Serial port for communication with Raspberry Pi
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  inputString.reserve(200);
  
  Serial.println("ESP32 WiFi Module Ready");
  Serial.println("Commands: CONNECT, DISCONNECT, STATUS, IP, SCAN");
  
  // Auto-connect to WiFi on startup
  connectToWiFi();
}

void loop() {
  // Handle serial commands from Raspberry Pi
  serialEvent();
  
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Monitor WiFi connection status
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck > 10000) { // Check every 10 seconds
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WARNING: WiFi disconnected. Attempting to reconnect...");
      connectToWiFi();
    }
    lastCheck = millis();
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command == CMD_CONNECT) {
    connectToWiFi();
  } 
  else if (command == CMD_DISCONNECT) {
    WiFi.disconnect();
    Serial.println("RESPONSE: WiFi disconnected");
  } 
  else if (command == CMD_STATUS) {
    sendStatus();
  } 
  else if (command == CMD_IP) {
    sendIPAddress();
  } 
  else if (command == CMD_SCAN) {
    scanNetworks();
  } 
  else {
    Serial.println("ERROR: Unknown command");
  }
}

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  Serial.print("CONNECTING: ");
  Serial.println(WIFI_SSID);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("CONNECTED: WiFi connection established");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("SIGNAL: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("ERROR: Failed to connect to WiFi");
  }
}

void sendStatus() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("STATUS: CONNECTED");
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("SIGNAL: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("STATUS: DISCONNECTED");
  }
}

void sendIPAddress() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("ERROR: Not connected to WiFi");
  }
}

void scanNetworks() {
  Serial.println("SCANNING: WiFi networks...");
  
  int n = WiFi.scanNetworks();
  
  if (n == 0) {
    Serial.println("SCAN: No networks found");
  } else {
    Serial.print("SCAN: Found ");
    Serial.print(n);
    Serial.println(" networks");
    
    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(" dBm) ");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? "Open" : "Encrypted");
      delay(10);
    }
  }
  
  Serial.println("SCAN: Complete");
}
