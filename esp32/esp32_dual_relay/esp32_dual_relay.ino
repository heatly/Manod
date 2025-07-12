#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "oppo";
const char* password = "12345678";

WebServer server(80);

const int relay1 = 5;
const int relay2 = 18;

bool relayOn1 = false;
bool relayOn2 = false;
unsigned long start1 = 0;
unsigned long start2 = 0;

void setup() {
  Serial.begin(115200);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\\nConnected to WiFi");

  server.on("/relay1/on", HTTP_GET, []() {
    digitalWrite(relay1, HIGH);
    relayOn1 = true;
    start1 = millis();
    server.send(200, "text/plain", "Relay 1 ON");
  });

  server.on("/relay1/off", HTTP_GET, []() {
    digitalWrite(relay1, LOW);
    relayOn1 = false;
    unsigned long runtime = (millis() - start1) / 1000;
    Serial.printf("Relay 1 OFF. Runtime: %lus\\n", runtime);
    server.send(200, "text/plain", "Relay 1 OFF. Runtime: " + String(runtime) + "s");
  });

  server.on("/relay2/on", HTTP_GET, []() {
    digitalWrite(relay2, HIGH);
    relayOn2 = true;
    start2 = millis();
    server.send(200, "text/plain", "Relay 2 ON");
  });

  server.on("/relay2/off", HTTP_GET, []() {
    digitalWrite(relay2, LOW);
    relayOn2 = false;
    unsigned long runtime = (millis() - start2) / 1000;
    Serial.printf("Relay 2 OFF. Runtime: %lus\\n", runtime);
    server.send(200, "text/plain", "Relay 2 OFF. Runtime: " + String(runtime) + "s");
  });

  server.begin();
  Serial.println("Web server started");
}

void loop() {
  server.handleClient();
}
