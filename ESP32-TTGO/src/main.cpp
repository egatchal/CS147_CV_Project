#include <WiFi.h>
#include <ArduinoHttpClient.h>
#include <Arduino.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <ArduinoJson.h>    // Include the JSON parsing library

// ===========================
// Enter your WiFi credentials
// ===========================
const char *ssid = "1474hahahahah";
const char *password = "Sunshine720@#88!";

// const char *ssid = "UCInet Mobile Access";
// const char *password = "";

const char* serverAddress = "3.143.245.72"; // Server address
const int serverPort = 8080;              // Server port (80 for HTTP, 443 for HTTPS)
WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, serverPort);
TFT_eSPI tft = TFT_eSPI();

void setupWifi() {
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.println(WiFi.macAddress());

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

// Function to print text in the center of the screen
void printCentered(const char* text) {
  tft.setTextDatum(MC_DATUM); // Middle center datum
  tft.setTextColor(TFT_WHITE, TFT_BLACK); // White text with black background
  tft.drawString(text, tft.width() / 2, tft.height() / 2); // Draw the string in the center
}

const int GREEN_LED_PIN = 17;
const int RED_LED_PIN = 15;
const int buttonPin = 33;  // the number of the pushbutton pin

// variables will change:
int buttonState = 0;  // variable for reading the pushbutton status


void setup() {
  Serial.begin(9600);
  Serial.setDebugOutput(false);

  Serial.println("Starting WiFi");
  setupWifi();
  Serial.println("WiFi connected");
  
  // For initializing the screen display
  tft.init();
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, 0xF080);
  
  // pinMode(GREEN_LED_PIN, OUTPUT);
  // pinMode(RED_LED_PIN, OUTPUT);

  // initialize the LED pin as an output:
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  buttonState = digitalRead(buttonPin);
  // Serial.println("GOT BUTTON STATE");
  if (buttonState == LOW) { // If button pressed
    tft.fillScreen(TFT_BLACK);
    Serial.println("Preparing to send post!");
  
    String jsonData = "{\"press\": \"True\"}";
    String contentType = "application/json";
    String postData = jsonData;

    Serial.println("Posting...");
    client.post("/api/button", contentType, postData);

    // read the status code and body of the response
    int statusCode = client.responseStatusCode();
    String response = client.responseBody();

    Serial.print("Status code: ");
    Serial.println(statusCode);
    Serial.print("Response: ");
    Serial.println(response);

    JsonDocument doc;
    deserializeJson(doc, response);
    if (doc["found"]) {
      // Get the names array
      JsonArray names = doc["names_of_person"];
      String namesString = "";
      
      // Concatenate all names into a single string
      for (JsonVariant v : names) {
        if (namesString.length() > 0) {
          namesString += ", ";
        }
        namesString += v.as<String>();
      }

      // Create the final output string
      String output = "MATCH: " + namesString;
      
      // Print the final output string
      printCentered(output.c_str());
    } else {
      printCentered("NO MATCH");
    }
  }
  delay(100);
}