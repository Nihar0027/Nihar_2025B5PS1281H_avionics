#include <LiquidCrystal.h>
int buttonoldval=1, buttonnewval , button=2,redled=3,buzzer=4,photosensor=A2,voltagevalue,trig=5,echo=6,RS=7,E=8,DB4=9,DB5=10;
int DB6=11,DB7=12,dt=50,anchor=0,count=0,storm=0,charybids=0,timetaken,dt1=10,sailing=1,wrecked=0;
long timer1=0,timer2=0,speedofsound=34300;
long conversionfactor=2000000;
float actualvoltage,distance;
LiquidCrystal lcd(RS,E,DB4,DB5,DB6,DB7);
void setup() {
   Serial.begin(9600);
  pinMode(button,INPUT);
  digitalWrite(button,HIGH);  
  pinMode(redled,OUTPUT);
  pinMode(buzzer,OUTPUT);
  pinMode(photosensor, INPUT);
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  lcd.begin(16,2);
}

void loop() {
  digitalWrite(trig,LOW);              //code for HC-SR04 sensor
  delayMicroseconds(dt1);
  digitalWrite(trig,HIGH);
    delayMicroseconds(dt1);
    digitalWrite(trig, LOW);
    timetaken=pulseIn(echo,HIGH);       //it measures the time it takes for the ultra sonic wave to leave the sensor and return back, so we need to divide by 2 to measure the distance.
    distance=(speedofsound*timetaken)/conversionfactor;
buttonnewval=digitalRead(button);
if(buttonnewval==0 && buttonoldval==1 && sailing==1 && wrecked==0)      //we need to make sure that it doesnt work when the ship is already down so i used wrecked==0, that is ship is down 
{          
  anchor=1;       //means the anchor is down
  sailing=0;       // this sells that ship is sailing
}
else if(buttonnewval==0 && buttonoldval==1 && sailing==0 && wrecked==0)  //for ships to sail once the anchor is up
{
  anchor=0;               //saves the state of the ship
  sailing=1;
}
buttonoldval=buttonnewval;        //so that we could avoid multiple inputs
if(wrecked==1 && anchor==0 && sailing==0)   
{
  lcd.setCursor(0,0);
  lcd.print("WRECKED.        ");      
}

else if(wrecked==0 && storm==1)
{
  lcd.setCursor(0,0);
  lcd.print("STORM!!        ");
}
else if(wrecked==0 && charybids==1)
{
  lcd.setCursor(0,0);
  lcd.print("CHARYBIDS!!         ");
}
else if(anchor==1 && sailing==0 && wrecked==0 )
{
    lcd.setCursor(0,0);
  lcd.print("ANCHOR DOWN.      ");

}
 else if(sailing==1 && anchor==0 && wrecked==0)
{
    lcd.setCursor(0,0);
  lcd.print("SAILING.         ");
}
voltagevalue=analogRead(photosensor);
if(voltagevalue <=479 && anchor==0)  //my photosensor went from 28 to 958, so i took 479 as middle ground ,, then if anchor is down no need to enter here
{
  if(storm==0)
  {
    timer1=millis();   //millis always run from the start, so i need to timer1=millis only when the storm starts , so i used this if statement otherwise it would have entered this if statement
     //multiple times ,and timer will always be equal to the millis , so later on i can not use it to find whether the time is greater than 5 sec or less
  }
  storm=1;
  
}
else if(distance<=100 && anchor==0)
{
  if(charybids==0)
  {
     timer2=millis();
  }
  charybids=1;
}

if(storm==1 && wrecked==0)             
{
  digitalWrite(redled,HIGH);
  if(anchor==0 && millis()-timer1<=5000 && voltagevalue >479)     //condition if storm goes within 5s, so i used voltage more than the threshold i.e half of maximum
  {
  storm=0;
sailing=1;
wrecked=0;
digitalWrite(redled,LOW);
}
else if(anchor==0 && millis()-timer1 > 5000 )    //if timer goes for more than 5 secs the ship is wrecked
{
  sailing=0;
  wrecked=1;
  storm=0;
  digitalWrite(redled,LOW);
}
else if(anchor==1 && millis()-timer1 <=5000)    //for ship to be safe withing 5 secs 
{
  sailing=0;
  wrecked=0;
  storm=0;
  digitalWrite(redled,LOW);
}

}
else if(charybids==1 && wrecked==0)   //Conditon for the charybids
{
digitalWrite(buzzer,HIGH);

  if(anchor==1 && millis()-timer2<=5000)
  {
    charybids=0;
    sailing=0;
    wrecked=0;
    digitalWrite(buzzer,LOW);
  
  }
  else if(anchor==0 && millis()-timer2<=5000 && distance >100)
  {
    charybids=0;
    sailing=1;
    wrecked=0;
    digitalWrite(buzzer,LOW);
  }
  else if( anchor==0 && millis()-timer2 >5000)
  {
    sailing=0;
    wrecked=1;
    charybids=0;
    digitalWrite(buzzer, LOW);
  }
}


}
