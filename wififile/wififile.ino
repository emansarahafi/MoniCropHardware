#include <WiFi.h>

// Define the WiFi network credentials
const char* WIFI_SSID = "INSERT_YOUR_SSID_HERE";
const char* WIFI_PASSWORD = "INSERT_YOUR_WIFI_PASSWORD_HERE";

void setup() {
  // Initialize the Serial port for debugging
  Serial.begin(115200);
 
  // Initialize the ESP32 WiFi module
  WiFi.mode(WIFI_STA);

  // Connect to the WiFi network
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);
  Serial.println("...");

  // Wait for the WiFi connection to be established
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  // Print the IP address assigned to the Raspberry Pi by the WiFi network
  Serial.println("");
  Serial.println("WiFi connection established.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // do nothing
}
