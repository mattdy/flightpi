#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define BRIGHTNESS 50

Adafruit_NeoPixel pixel_dir = Adafruit_NeoPixel(16, 2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel pixel_liv = Adafruit_NeoPixel(24, 3, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel pixel_alt = Adafruit_NeoPixel(16, 4, NEO_GRB + NEO_KHZ800);

// The actual bulbs aren't in a nice order, so set up arrays to determine which order to light them up in
int dirBulbs[] = { 6,5,4,3,2,1,0,15,14,13,12,11,10,9,8,7 };
int altBulbs[] = { 7,15,6,14,5,13,4,12,3,11,2,10,1,9,0,8 };

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

void processValue(String val) {
  Serial.print("Processing ");
  Serial.println(val);

  switch(val[0]) {
    case 'D': {
      setDirection(val.substring(1).toInt());
    } break;

    case 'A': {
      setAltitude(val.substring(1).toInt());
    } break;

    case 'L': {
      //TODO: Livery display
    } break;

    case 'C': {
      clear();
    } break;
  }
}

void setDirection(int direction) {
  int pixels = 1 + (direction / 22.5);

  Serial.print("Direction: ");
  Serial.print(direction);
  Serial.print(", Pixels: ");
  Serial.println(pixels);

  for(uint16_t i=0; i<pixel_dir.numPixels(); i++) {
    if(i<pixels) {
      pixel_dir.setPixelColor(dirBulbs[i], pixel_dir.Color(0,0,255));
    } else {
      pixel_dir.setPixelColor(dirBulbs[i], pixel_dir.Color(0,0,0));
    }
  }

  pixel_dir.show();
}

void setAltitude(int level) {
  int pixels = level / 500; // One LED per 500ft

  Serial.print("Altitude: ");
  Serial.print(level);
  Serial.print(", Pixels: ");
  Serial.println(pixels);
          
  if(pixels>pixel_alt.numPixels()) { pixels = pixel_alt.numPixels(); }

  for(uint16_t i=0; i<pixel_alt.numPixels(); i++) {
    if(i<pixels) {
      pixel_alt.setPixelColor(altBulbs[i], pixel_alt.Color(0,0,255));
    } else {
      pixel_alt.setPixelColor(altBulbs[i], pixel_alt.Color(0,0,0));
    }
  }

  pixel_alt.show();
}

void clear() {
  Serial.println("Clearing");

  for(uint16_t i=0; i<pixel_dir.numPixels(); i++) {
    pixel_dir.setPixelColor(i, pixel_dir.Color(0,0,0));
  }
  pixel_dir.show();

  for(uint16_t i=0; i<pixel_alt.numPixels(); i++) {
    pixel_alt.setPixelColor(i, pixel_alt.Color(0,0,0));
  }
  pixel_alt.show();
}

void loop() {
  String data;

  while (Serial.available() > 0) {
    char received = Serial.read();

    Serial.print("Got [");
    Serial.print(received);
    Serial.println("]");

    data += received;

    // Process message when new line character is recieved
    if(received == '\n') {
      processValue(data);
      data = "";
    }
  }

  delay(100);
}
