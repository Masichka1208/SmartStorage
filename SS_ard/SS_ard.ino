// SLAVE

#include <Wire.h>

#define STRIP_PIN 4  // пин ленты
#define NUMLEDS 8    // кол-во светодиодов
#define COLOR_DEBTH 3

#include <microLED.h>

microLED<NUMLEDS, STRIP_PIN, MLED_NO_CLOCK, LED_WS2818, ORDER_GRB, CLI_AVER> strip;

byte i2c_rcv;              // data received from I2C bus
unsigned long time_start;  // start time in mSec
int stat_LED;              // status of LED: 1 = ON, 0 = OFF
byte value_pot;            // potentiometer position

void setup() {
  strip.setBrightness(120);
  Wire.begin(0x08);  // join I2C bus as Slave with address 0x08
  Serial.begin(9600);

  // event handler initializations
  Wire.onReceive(dataRcv);   // register an event handler for received data
  Wire.onRequest(dataRqst);  // register an event handler for data requests

  // initialize global variables
  i2c_rcv = 255;
  time_start = millis();
  stat_LED = 0;

  pinMode(13, OUTPUT);  // set pin 13 mode to output
}

void loop() {

  value_pot = analogRead(A0);  // read analog value at pin A0 (potentiometer voltage)

  // blink logic code
  if ((millis() - time_start) > (1000 * (float)(i2c_rcv / 255))) {
    stat_LED = !stat_LED;
    time_start = millis();
  }
  digitalWrite(13, stat_LED);
}

//received data handler function
void dataRcv(int numBytes) {
  uint8_t counter = 0;
  uint8_t data[] = { 0, 0, 0, 0 };
  while (Wire.available()) {  // read all bytes received
    i2c_rcv = Wire.read();
    data[counter] = i2c_rcv;
    counter += 1;
    Serial.print(counter);
    Serial.print("  ");
    Serial.println(i2c_rcv);
  }
  strip.set(data[0], mRGB(data[1], data[2], data[3]));
  strip.show();
}

// requests data handler function
void dataRqst() {
  Wire.write(value_pot);  // send potentiometer position
}
