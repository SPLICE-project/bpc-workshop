#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

using namespace std; 

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET     -1 // Reset pin # ( -1 to share rESET PIN)

/******----- FOR THERMOMETER-----------------*/
const int oneWireBus = 15; // Data wire is conneted to port 15 in ESP32
OneWire oneWire(oneWireBus); // Create instance of oneWire
DallasTemperature sensors(&oneWire); // Pass oneWire instance to Dallas Temperature sensor

/********------- FOR SCREEN-----------*/
// SSD1306 display connected to I2C (SDA, SCL pins)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//WiFi AP 
const char* ssid = "SPLICE_DEMO_TWO";
const char* password ="splice24";


volatile float temperatureC = 0.0;
volatile float temperatureF = 0.0;
SemaphoreHandle_t tempMutex;

void TaskReadTemperature(void* parameter) {
  for (;;) {
    // Get temp reading
    sensors.requestTemperatures();
    xSemaphoreTake(tempMutex, portMAX_DELAY);
    temperatureC = sensors.getTempCByIndex(0);
    temperatureF = sensors.getTempFByIndex(0);
    xSemaphoreGive(tempMutex);

    // Wait a bit before reading again
    vTaskDelay(5000 / portTICK_PERIOD_MS);
  }
}

void TaskDisplayOLED(void* parameter) {
  for (;;) {
    char temp_cels[50];
    char temp_far[50];

    xSemaphoreTake(tempMutex, portMAX_DELAY);
    sprintf(temp_cels, "%.2f C", temperatureC);
    sprintf(temp_far, "%.2f F", temperatureF);
    xSemaphoreGive(tempMutex);

    display.clearDisplay();
    display.setTextSize(3);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.println("TEMP:");
    display.setTextSize(2);
    display.setCursor(0, 17);
    display.println(temp_far);
    display.println(temp_cels);
    display.display();

    vTaskDelay(100/ portTICK_PERIOD_MS);
  }
}

void TaskSendHTTP(void* parameter) {
  for (;;) {
    if(WiFi.status() == WL_CONNECTED) {
      // Create a JSON object
      StaticJsonDocument<200> doc;
      char jsonBuffer[512];

      xSemaphoreTake(tempMutex, portMAX_DELAY);
      doc["temperatureC"] = temperatureC;
      doc["temperatureF"] = temperatureF;
      xSemaphoreGive(tempMutex);

      // Serialize the JSON object into a buffer
      serializeJson(doc, jsonBuffer, sizeof(jsonBuffer));

      HTTPClient http;
      http.begin("http://192.168.5.1:5000/data"); 
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(jsonBuffer);

      if (httpResponseCode > 0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      }
      else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }

      http.end();
    }
    vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}



void setup() {
  Serial.begin(115200); // start serial monitor
  sensors.begin(); // start Dallas Temperature sensor

  //check display volatage
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("SSD1306 allocation failed"));
    while(1){continue;} // loop forever
  }

  display.display(); // display buffer contents
  delay(2000);       // pause for 2 seconds
  display.clearDisplay(); // clean buffer

  //connect to Wi-Fi 
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Trying to connect to WiFi network....");

  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(100);
  }

  Serial.println("\nConnected to WiFi");
  Serial.println("IP is:");
  Serial.println(WiFi.localIP());

  tempMutex = xSemaphoreCreateMutex();

  xTaskCreatePinnedToCore(
    TaskReadTemperature, "TaskReadTemperature", 2048, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(
    TaskDisplayOLED, "TaskDisplayOLED", 2048, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(
    TaskSendHTTP, "TaskSendHTTP", 4096, NULL, 1, NULL, 1);

}

void loop() {
}
