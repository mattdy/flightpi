#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define BRIGHTNESS 50

Adafruit_NeoPixel pixel_dir = Adafruit_NeoPixel(16, 2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel pixel_liv = Adafruit_NeoPixel(24, 3, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel pixel_alt = Adafruit_NeoPixel(16, 4, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);

  pixel_dir.setBrightness(BRIGHTNESS);
  pixel_liv.setBrightness(BRIGHTNESS);
  pixel_alt.setBrightness(BRIGHTNESS);

  pixel_dir.begin();
  pixel_liv.begin();
  pixel_alt.begin();

  pixel_dir.show();
  pixel_liv.show();
  pixel_alt.show();
}

void loop() {
  if (Serial.available() > 0) {
    String incoming = Serial.readString();

    switch(incoming[0]) {
      case 'D': {
          int direction = incoming.substring(1).toInt();
          int pixels = direction / 22.5;

          Serial.print("Direction: ");
          Serial.print(direction);
          Serial.print(", Pixels: ");
          Serial.println(pixels);

          for(uint16_t i=0; i<pixel_dir.numPixels(); i++) {
            if(i<pixels) {
              pixel_dir.setPixelColor(i, pixel_dir.Color(0,0,255));
            } else {
              pixel_dir.setPixelColor(i, pixel_dir.Color(0,0,0));
            }
          }

          pixel_dir.show();
      } break;

      case 'L': {

      } break;


      case 'A': {

      } break;
    } // switch
  }
  
  delay(100);
}
