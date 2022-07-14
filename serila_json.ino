double Fahrenheit(double celsius) 
{
        return 1.8 * celsius + 32;
}    //摄氏温度度转化为华氏温度

double Kelvin(double celsius)
{
        return celsius + 273.15;
}     //摄氏温度转化为开氏温度


#include <dht11.h>

dht11 DHT11;

#define DHT11PIN 4
#define MQ5PIN 3
#define LIGHTPIN 2
#define LEDPIN 5
#define PWMPIN 6
#define YLPIN 7
int MQ5Pin = A0; 
int LIGHTPin = A1;
int YLPin=A2;
int PWM=0;


void readdht11()
{
  int chk = DHT11.read(DHT11PIN);

  //Serial.print("Read sensor: ");
  switch (chk)
  {
    case DHTLIB_OK: 
                //Serial.println("OK"); 
                break;
    case DHTLIB_ERROR_CHECKSUM: 
                Serial.print("Checksum error"); 
                break;
    case DHTLIB_ERROR_TIMEOUT: 
                Serial.print("Time out error"); 
                break;
    default: 
                Serial.print("Unknown error"); 
                break;
  }
  Serial.print("\"humidity\":\"");
  Serial.print((float)DHT11.humidity, 2);

  Serial.print("\",\"temperature\":\"");
  Serial.print((float)DHT11.temperature, 2);
  Serial.print("\",");
}

void readmq5()
{
  int state=0;
  float value=0;
  state=digitalRead(MQ5PIN);  
  Serial.print("\"mq5warning\":");
  if (state == HIGH) {
    Serial.print("\"N\",");
  } else {
    Serial.print("\"Y\",");
  }
  value = analogRead(MQ5Pin)*100/1024;
  Serial.print("\"gas density\":\"");
  Serial.print(value);
  Serial.print("\",");
}

void readlight(){
  int state=0;
  float value=0;
  state=digitalRead(LIGHTPIN); 
  Serial.print("\"indoor\":"); 
  if (state == HIGH) {
    Serial.print("\"Dark\",");
  } else {    
    Serial.print("\"Bright\",");
  }
  value=(float)analogRead(LIGHTPin)*0.098;
  Serial.print("\"light_intensity\":\"");
  Serial.print(value);
  Serial.print("\",");
}

void ledread(){
   int state=0;
  state=digitalRead(LEDPIN);  
  Serial.print("\"ledstate\":");
  if (state == HIGH) {
    Serial.print("\"Led closed\",");
  } else {    
    Serial.print("\"Led opened\",");
  }
}

void ledcontrol(char cmd){
  if(cmd=='o'){
    digitalWrite(LEDPIN, LOW);
    Serial.println("Led opened.");
  }     
  else if(cmd=='c'){
    digitalWrite(LEDPIN, HIGH);
    Serial.println("Led closed.");
  }      
}

void PWMread(){
  
  Serial.print("\"PWM\":\"");
  Serial.print(PWM);
  Serial.print("\",");
}

void PWMcontrol(String comdata){
  char bai = comdata[1];
  char shi = comdata[2];
  char ge = comdata[3];
  bai=bai-'0';
  shi=shi-'0';
  ge=ge-'0';
  PWM=bai*100+shi*10+ge;
  if((PWM>=0)&&(PWM<=254)){
    analogWrite(PWMPIN, PWM);
    Serial.print("PWM=");
    Serial.print(PWM);
    Serial.println('.');
  }
  else{
     Serial.println("PWM out of range");
  }
   
}

void YLread(){
  int state=0;
  float value=0;
  state=digitalRead(YLPIN); 
  Serial.print("\"soil_state\":"); 
  if (state == HIGH) {
    Serial.print("\"Soil Dry\",");
  } else {    
    Serial.print("\"Soil Moist\",");
  }
  value=(float)analogRead(YLPin)*0.098;
  Serial.print("\"soilHydropenia\":\"");
  Serial.print(value);
  Serial.print("\"");
}


void sensor_read(){
  Serial.print("{");
  readdht11();
  readmq5();
  readlight();
  ledread();
  PWMread();
  YLread();
  Serial.println("}");
}

String comdata = "";

void setup()
{
  Serial.begin(9600);
  pinMode(MQ5PIN, INPUT);
  pinMode(LIGHTPIN, INPUT);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, HIGH);
}

void loop()
{
  while (Serial.available() > 0)  
    {
        comdata += char(Serial.read());
        delay(2);
    }
    if (comdata.length() > 0)
    {
        char cmd=comdata[0];
        if(cmd=='o'||cmd=='c')
          ledcontrol(cmd);
        else if(cmd=='a')
          sensor_read();
        else if(cmd=='p'){
          if (comdata.length()==4)
            PWMcontrol(comdata);
        }         
        comdata = "";
    }
  
}
