#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoHttpClient.h>
#include <base64.h>
// ===================
// Select camera model
// ===================
#define CAMERA_MODEL_AI_THINKER // Has PSRAM

// #define PWDN_GPIO_NUM 32
// #define RESET_GPIO_NUM -1
// #define XCLK_GPIO_NUM 0
// #define SIOD_GPIO_NUM 26
// #define SIOC_GPIO_NUM 27

// #define Y9_GPIO_NUM 35
// #define Y8_GPIO_NUM 34
// #define Y7_GPIO_NUM 39
// #define Y6_GPIO_NUM 36
// #define Y5_GPIO_NUM 21
// #define Y4_GPIO_NUM 19
// #define Y3_GPIO_NUM 18
// #define Y2_GPIO_NUM 5
// #define VSYNC_GPIO_NUM 25
// #define HREF_GPIO_NUM 23
// #define PCLK_GPIO_NUM 22
#include "camera_pins.h"

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

camera_config_t config;
void cameraInit() {
// #define PWDN_GPIO_NUM 32
// #define RESET_GPIO_NUM -1
// #define XCLK_GPIO_NUM 0
// #define SIOD_GPIO_NUM 26
// #define SIOC_GPIO_NUM 27

// #define Y9_GPIO_NUM 35
// #define Y8_GPIO_NUM 34
// #define Y7_GPIO_NUM 39
// #define Y6_GPIO_NUM 36
// #define Y5_GPIO_NUM 21
// #define Y4_GPIO_NUM 19
// #define Y3_GPIO_NUM 18
// #define Y2_GPIO_NUM 5
// #define VSYNC_GPIO_NUM 25
// #define HREF_GPIO_NUM 23
// #define PCLK_GPIO_NUM 22
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 2;
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA); // 320x240
  }

  // #if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  //   s->set_vflip(s, 1);
  //   s->set_hmirror(s, 1);
  // #endif

  // #if defined(CAMERA_MODEL_ESP32S3_EYE)
  //   s->set_vflip(s, 1);
  // #endif

  // // Setup LED FLash if LED pin is defined in camera_pins.h
  // #if defined(LED_GPIO_NUM)
  //   setupLedFlash(LED_GPIO_NUM);
  // #endif
}

void setupWifi() {
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.println(WiFi.macAddress());

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
}

String grabImage() {
  camera_fb_t *fb = NULL;
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    esp_camera_fb_return(fb);
    fb = NULL;
    return "";
  }
  // Convert the image data to base64
  String base64String = base64::encode(fb->buf, fb->len);
  esp_camera_fb_return(fb);
  fb = NULL;
  return base64String;
}

bool buttonPressed = false;
const int LED_PIN = 4;

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println("Initializing camera");
  cameraInit();
  Serial.println("Camera initialized!");
  
  Serial.println("Starting WiFi");
  setupWifi();

  pinMode(LED_PIN, OUTPUT);
}


bool firstTime = true;
void loop() {
  // camera_fb_t *fb = NULL;
  // esp_err_t res = ESP_OK;
  // fb = esp_camera_fb_get();
  // if(!fb) {
  //   Serial.println("Camera capture failed");
  //   esp_camera_fb_return(fb);
  //   return;
  // }

  // size_t fb_len = 0;
  
  // if(fb->format != PIXFORMAT_JPEG){
  //   Serial.println("Non-JPEG data not implemented");
  //   return;
  // }
  // Serial.println("Button pressed!");
  // digitalWrite(ledPin, HIGH);
  // delay(100);
  String encodedImage = grabImage();

  if (encodedImage.equals("")) {
    Serial.println("Could not grab image!");
    return;
  }

  Serial.println("Preparing to send post!");
  String pixelDataString = encodedImage;
  String jsonData = "{\"image\":";
  jsonData.concat("\"" + pixelDataString + "\"");
  jsonData.concat("}");
  Serial.println("making POST request");

  String contentType = "application/json";
  String postData = jsonData;

  Serial.println("Posting...");
  client.post("/api/upload", contentType, postData);

  // read the status code and body of the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Status code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);

  // delay(100);
  // digitalWrite(ledPin, LOW);
  // buttonPressed = false;
  Serial.println("Wait 5 seconds");
  delay(5000);
  // if (buttonPressed) {
  //   Serial.println("Button pressed!");
  //   digitalWrite(ledPin, HIGH);
  //   delay(100);
  //   String base64String = grabImage();
  //   delay(100);
  //   digitalWrite(ledPin, LOW);
  //   buttonPressed = false;
  // }
}
