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

// Fetch colour based on character value
uint32_t getColor(char val) {
  switch(val) {
    case 'R': return pixel_liv.Color(255, 0  , 0  );
    case 'G': return pixel_liv.Color(0  , 255, 0  );
    case 'B': return pixel_liv.Color(0  , 0  , 255);
    case 'W': return pixel_liv.Color(255, 255, 255);
    case 'Y': return pixel_liv.Color(255, 255, 0  );
    case 'O': return pixel_liv.Color(255, 128, 0  );
    case 'N':
    default:
      return pixel_liv.Color(0,0,0);

  }
}

void processValue(String val) {
  Serial.print("Processing ");
  Serial.println(val);

  switch(val[0]) {
    case 'D': {
      setDirection(val.substring(1).toInt());
    } break;

    case 'A': {
      setAltitude(val.substring(2).toInt(), val[1]);
    } break;

    case 'L': {
      setLivery(val.substring(1));
    } break;

    case 'C': {
      clear();
    } break;
  }
}

void setLivery(String colours) {
  Serial.print("Livery: ");
  Serial.println(colours);

  int pixPerCol = pixel_liv.numPixels() / 3;
  for(uint16_t i=0; i<3; i++) {
    uint32_t c = getColor(colours[i]);
    for(uint16_t p=0; p<pixPerCol; p++) {
      pixel_liv.setPixelColor(((2-i) * pixPerCol) + p, c);
    }
  }

  pixel_liv.show();
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

void setAltitude(int level, char climb) {
  int pixels = level / 500; // One LED per 500ft

  Serial.print("Altitude: ");
  Serial.print(level);
  Serial.print(", Climb: ");
  Serial.print(climb);
  Serial.print(", Pixels: ");
  Serial.println(pixels);
          
  if(pixels>pixel_alt.numPixels()) { pixels = pixel_alt.numPixels(); }

  uint32_t col;
  switch(climb) {
    case 'C':
      col = pixel_alt.Color(0,255,0);
      break;

    case 'D':
      col = pixel_alt.Color(255,0,0);
      break;

    case 'L':
    default:
      col = pixel_alt.Color(0,0,255);
    break;
  }

  for(uint16_t i=0; i<pixel_alt.numPixels(); i++) {
    if(i<pixels) {
      pixel_alt.setPixelColor(altBulbs[i], col);
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

  for(uint16_t i=0; i<pixel_liv.numPixels(); i++) {
    pixel_liv.setPixelColor(i, pixel_liv.Color(0,0,0));
  }
  pixel_liv.show();
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
