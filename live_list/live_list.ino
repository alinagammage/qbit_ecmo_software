void setup() {
  Serial.begin(9600);
}

void loop() {
  int values[7];
  
  // Generate random values
  for (int i = 0; i < 7; i++) {
    values[i] = random(0, 100);  // Generate random values between 0 and 99
  }
  
  // Print values in the desired format
  Serial.print("[");
  for (int i = 0; i < 7; i++) {
    Serial.print(values[i]);
    if (i < 6) {
      Serial.print(", ");
    }
  }
  Serial.println("]");
  
  delay(100);  // Delay for 100 milliseconds (0.1 seconds)
}

