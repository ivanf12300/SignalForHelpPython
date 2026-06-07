void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

void loop() {
    if (Serial.available()) {
        char valor = Serial.read();
        if (valor == '1'){
            digitalWrite(13, HIGH);
        }else if(valor == '0'){
            digitalWrite(13, LOW);
        } 
    }
}