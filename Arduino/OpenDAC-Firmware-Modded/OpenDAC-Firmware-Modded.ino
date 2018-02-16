//Ardunio *DUE*code for controlling EVAL-AD7734 ADC and EVAL-AD5764 DAC
//Created by Andrea Young
//Modified by Carlos Kometter 7/7/2015
//Modified by Joe Sheldon 11/03/2017

#include "SPI.h" // necessary library for SPI communication
#include <vector>
//include <MemoryFree.h>;

int adc = 52; //The SPI pin for the ADC
int dac = 4; //The SPI pin for the DAC
int ldac = 6; //Load DAC pin for DAC. Make it LOW if not in use.
int clr = 5; // Asynchronous clear pin for DAC. Make it HIGH if you are not using it
int reset = 44 ; //Reset on ADC
int drdy = 48; // Data is ready pin on ADC
int led = 32;
int data = 28; //Used for trouble shooting; connect an LED between pin 13 and GND
int err = 30;
const int Noperations = 18;
String operations[Noperations] = {"NOP", "SET", "GET_ADC", "RAMP1", "RAMP2", "BUFFER_RAMP", "RESET", "TALK", "CONVERT_TIME", "*IDN?", "*RDY?", "RAR1", "SIN", "ACQA","RARA","SRAMF","ACQ1","SIN4"};

//Custom Buffer Functions. Buffer should be in the stack.
const int bufferv_xdim = 4;
const int bufferv_ydim = 5000;
float bufferv[bufferv_xdim][bufferv_ydim]; //4 channel voltage buffer. Should be 80,000 bytes long.

//Initializes buffer to 0s.
void clearbuffer(float arr[bufferv_xdim][bufferv_ydim])
{
  for(int x = 0;x < bufferv_xdim;x++)
  {
    for(int y = 0;y < bufferv_ydim;y++)
    {
      arr[x][y]=0;
    }
  }
}

//linearly writes to buffer. (1ch acq)
void linearWriteToBuffer(float arr[bufferv_xdim][bufferv_ydim],int linpos,float valToWrite)
{
  int xidx = floor( linpos / bufferv_ydim);
  int yidx = linpos - (xidx * bufferv_ydim);

  arr[xidx][yidx] = valToWrite;
}

//doubly writes to buffer (2ch acq)
/*  Striping Pattern:
 *   (example 4x4 array)
 *  X across, Y down
 *    0   1   2   3
 *  0 A0  A2  A4  A6
 *  1 B0  B2  B4  B6
 *  2 A1  A3  A5  A7
 *  3 B1  B3  B5  B7
 */
void dualWriteToBuffer(float arr[bufferv_xdim][bufferv_ydim],int samplenumber,float chAval, float chBval)
{
  //samplenumber being the sample number. A# B# being ideally simult. measurements and # being the sample number
  xidx = floor((2*samplenumber) / (bufferv_ydim)); //Gives x coord of storage buffer
  yidxA = ((2*samplenumber) % bufferv_ydim); //Gives y coord of storage buffer for A
  yidxB = yidxA + 1; //Gives y coord of storage buffer for B

  arr[xidx][yidxA] = chAval;
  arr[xidx][yidxB] = chBval;
}

//writes 4 values to buffer. (4ch acq)
void quadWriteToBuffer(float arr[bufferv_xdim][bufferv_ydim],int buffpos,float ch0val, float ch1val, float ch2val, float ch3val)
{
  arr[0][buffpos] = ch0val;
  arr[1][buffpos] = ch1val;
  arr[2][buffpos] = ch2val;
  arr[3][buffpos] = ch3val;
}

//Reads Buffer in Linear Fashion
void linearReadBuffer(float arr[bufferv_xdim][bufferv_ydim],int linlen)
{
  int xpos;
  int ypos;

  //Print out voltages in a single, comma delimited line
  for (int linpos = 0; linpos < linlen; linpos++)
  {
    //Convert linear position to 2D position
    xpos = floor(linpos / bufferv_ydim);
    ypos = linpos - (xpos * bufferv_ydim);

    Serial.print(arr[xpos][ypos],8);
    Serial.flush();
    if (linpos != linlen - 1)
    {
      Serial.print('\n');
    }
  }
  //Serial.println(' ');
}

//Reads buffer out in 2 columns (ch: A  B)
void dualReadBuffer(float arr[bufferv_xdim][bufferv_ydim],int numbersamples)
{
  int xextent = floor(2*numbersamples / bufferv_ydim)
  
  for (int xpos = 0; xpos < numbersamples; xpos++)
  {
    for(int xpos = 0;xpos<xextent;xpos++)
    {
      Serial.print(arr[xpos][ypos],8);
      Serial.flush();
      if (xpos != bufferv_xdim - 1)
      {
        Serial.print(',');
      }
      else
      {
        Serial.print("\n");
      }
    }
    //Serial.println(' ');
  }
}


//Reads buffer out in 4 columns (ch: 0  1  2  3):
void quadReadBuffer(float arr[bufferv_xdim][bufferv_ydim],int linlen)
{

  for (int ypos = 0; ypos < linlen; ypos++)
  {
    for(int xpos = 0;xpos<bufferv_xdim;xpos++)
    {
      Serial.print(arr[xpos][ypos],8);
      Serial.flush();
      if (xpos != bufferv_xdim - 1)
      {
        Serial.print(',');
      }
      else
      {
        Serial.print("\n");
      }
    }
    //Serial.println(' ');
  }
}

//End Custom Buffer Functions

namespace std {
void __throw_bad_alloc()
{
  Serial.println("Unable to allocate memory");
}

void __throw_length_error( char const*e )
{
  Serial.print("Length Error :");
  Serial.println(e);
}
}


void setup()
{
  Serial.begin(115200);
  pinMode(ldac, OUTPUT);
  digitalWrite(ldac, LOW); //Load DAC pin for DAC. Make it LOW if not in use.
  pinMode(clr, OUTPUT);
  digitalWrite(clr, HIGH); // Asynchronous clear pin for DAC. Make it HIGH if you are not using it
  pinMode(reset, OUTPUT);
  pinMode(drdy, INPUT);  //Data ready pin for the ADC.
  pinMode(led, OUTPUT);  //Used for blinking indicator LED
  digitalWrite(led, HIGH);
  pinMode(data, OUTPUT);

  digitalWrite(reset, HIGH);  digitalWrite(data, LOW); digitalWrite(reset, LOW);  digitalWrite(data, HIGH); delay(5);  digitalWrite(reset, HIGH);  digitalWrite(data, LOW); //Resets ADC on startup.

  SPI.begin(adc); // wake up the SPI bus for ADC
  SPI.begin(dac); // wake up the SPI bus for ADC

  SPI.setBitOrder(adc, MSBFIRST); //correct order for AD7734.
  SPI.setBitOrder(dac, MSBFIRST); //correct order for AD5764.
  SPI.setClockDivider(adc, 84); //This can probably be sped up now that the rest of the code is better optimized. Limited by ADC
  SPI.setClockDivider(dac, 84); //This can probably be sped up now that the rest of the code is better optimized. Limited by ADC
  SPI.setDataMode(adc, SPI_MODE3); //This should be 3 for the AD7734
  SPI.setDataMode(dac, SPI_MODE1); //This should be 1 for the AD5764

  // Disables DAC_SDO to avoid interference with ADC
  SPI.transfer(dac, 1, SPI_CONTINUE);
  SPI.transfer(dac, 0, SPI_CONTINUE);
  SPI.transfer(dac, 1);

  //Initialize buffer to 0s:
  clearbuffer(bufferv);
}

void blinker(int s) {
  digitalWrite(data, HIGH);
  delay(s);
  digitalWrite(data, LOW);
  delay(s);
}
void sos() {
  blinker(50);
  blinker(50);
  blinker(50);
  blinker(500);
  blinker(500);
  blinker(500);
  blinker(50);
  blinker(50);
  blinker(50);
}

void error()
{
  digitalWrite(err, HIGH);
  delay(3000);
  digitalWrite(err, LOW);
  delay(500);
}


int indexOfOperation(String operation)
{
  for (int index = 0; index < Noperations; index++)
  {
    if (operations[index] == operation)
    {
      return index;
    }
  }
  return 0;
}

void waitDRDY() {
  while (digitalRead(drdy) == HIGH) {}
}

void resetADC() //Resets the ADC, and sets the range to default +-10 V
{
  digitalWrite(data, HIGH); digitalWrite(reset, HIGH); digitalWrite(reset, LOW); digitalWrite(reset, HIGH);
  SPI.transfer(adc, 0x28);
  SPI.transfer(adc, 0);
  SPI.transfer(adc, 0x2A);
  SPI.transfer(adc, 0);
}

void talkADC(std::vector<String> DB)
{
  int comm;
  comm = SPI.transfer(adc, DB[1].toInt());
  Serial.println(comm);
  Serial.flush();
}

int numberOfChannels(byte DB) // Returns the number of channels to write
{
  int number = 0;

  for (int i = 0; i <= 3; i++)
  {
    if (((DB >> i) & 1) == 1)
    {
      number++;
    }
  }
  return number;
}

std::vector<int> listOfChannels(byte DB) // Returns the list of channels to write
{
  std::vector<int> channels;

  int channel = 0;
  for (int i = 3; i >= 0; i--)
  {
    if (((DB >> i) & 1) == 1)
    {
      channels.push_back(channel);
    }
    channel++;
  }
  return channels;
}

void writeADCConversionTime(std::vector<String> DB)
{

  int adcChannel;
  switch (DB[1].toInt()) {
    case 0:
      adcChannel = 1;
      break;
    case 1:
      adcChannel = 3;
      break;
    case 2:
      adcChannel = 0;
      break;
    case 3:
      adcChannel = 2;
      break;

    default:
      break;
  }
  byte cr;

  byte fw = ((byte)(((DB[2].toFloat() * 6.144 - 249) / 128) + 0.5)) | 128;

  SPI.transfer(adc, 0x30 + adcChannel);
  SPI.transfer(adc, fw);
  delayMicroseconds(100);
  SPI.transfer(adc, 0x70 + adcChannel);
  cr = SPI.transfer(adc, 0); //Read back the CT register

  int convtime = ((int)(((cr & 127) * 128 + 249) / 6.144) + 0.5);
  //Serial.println(convtime);
  //Serial.print("\n");
}

float map2(float x, long in_min, long in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

int twoByteToInt(byte DB1, byte DB2) // This gives a 16 bit integer (between +/- 2^16)
{
  return ((int)((DB1 << 8) | DB2));
}


void intToTwoByte(int s, byte * DB1, byte * DB2)
{
  *DB1 = ((byte)((s >> 8) & 0xFF));
  *DB2 = ((byte)(s & 0xFF));
}


float twoByteToVoltage(byte DB1, byte DB2)
{
  int decimal;
  float voltage;

  decimal = twoByteToInt(DB1, DB2);

  if (decimal <= 32767)
  {
    voltage = decimal * 10.0 / 32767;
  }
  else
  {
    voltage = -(65536 - decimal) * 10.0 / 32768;
  }
  return voltage;
}


void voltageToTwoByte(float voltage, byte * DB1, byte * DB2)
{
  int decimal;
  if (voltage > 10 || voltage < -10)
  {
    *DB1 = 128;
    *DB2 = 0;
    error();
  }
  else if (voltage >= 0)
  {
    decimal = voltage * 32767 / 10;
  }
  else
  {
    decimal = voltage * 32768 / 10 + 65536;
  }
  intToTwoByte(decimal, DB1, DB2);
}

float getSingleReading(int adcchan)
{
  Serial.flush();
  int statusbyte = 0;
  byte o2;
  byte o3;
  int ovr;
  if (adcchan <= 3)
  {
    SPI.transfer(adc, 0x38 + adcchan); // Indicates comm register to access mode register with channel
    SPI.transfer(adc, 0x48);          // Indicates mode register to start single convertion in dump mode
    waitDRDY();                       // Waits until convertion finishes
    SPI.transfer(adc, 0x48 + adcchan); // Indcates comm register to read data channel data register
    statusbyte = SPI.transfer(adc, 0); // Reads Channel 'ch' status
    o2 = SPI.transfer(adc, 0);        // Reads first byte
    o3 = SPI.transfer(adc, 0);        // Reads second byte
    ovr = statusbyte & 1;
    switch (ovr)
    {
      case 0:
        int decimal;
        decimal = twoByteToInt(o2, o3);
        float voltage;
        voltage = map2(decimal, 0, 65536, -10.0, 10.0);
        return voltage;
        break;

      case 1:
        return 0.0;
        break;
    }
  }
}

float readADC(byte DB)
{
  int adcChannel = DB;
  switch (adcChannel)
  {
    case 0:
      return getSingleReading(1);
      break;
    case 1:
      return getSingleReading(3);
      break;
    case 2:
      return getSingleReading(0);
      break;
    case 3:
      return getSingleReading(2);
      break;

    default:
      break;
  }
}

float dacDataSend(int ch, float voltage)
{
  byte b1;
  byte b2;

  voltageToTwoByte(voltage, &b1, &b2);
  SPI.transfer(dac, 16 + ch, SPI_CONTINUE); // Indicates to DAC to write channel 'ch' in the data register
  SPI.transfer(dac, b1, SPI_CONTINUE); // writes first byte
  SPI.transfer(dac, b2);               // writes second byte
  return twoByteToVoltage(b1, b2);
}

float writeDAC(int dacChannel, float voltage)
{
  switch (dacChannel)
  {
    case 0:
      return dacDataSend(2, voltage);
      break;

    case 1:
      return dacDataSend(0, voltage);
      break;

    case 2:
      return dacDataSend(3, voltage);
      break;

    case 3:
      return dacDataSend(1, voltage);
      break;

    default:
      break;
  }
}

void readingRampAvg(int adcchan, byte b1, byte b2, byte * o1, byte * o2, int count, int nReadings)
{
  Serial.flush();
  int statusbyte = 0;
  int ovr;
  byte db1;
  byte db2;
  float sum = 0;
  float avg;
  bool toSend = true;
  if (adcchan <= 3)
  {
    for (int i = 1; i <= nReadings; i++)
    {
      SPI.transfer(adc, 0x38 + adcchan); // Indicates comm register to access mode register with channel
      SPI.transfer(adc, 0x48);          // Indicates mode register to start single convertion in dump mode
      if (count > 0 && toSend)
      {
        Serial.write(b1);                 // Sends previous reading while it is waiting for new reading
        Serial.write(b2);
        toSend = false;
      }
      waitDRDY();                       // Waits until convertion finishes
      SPI.transfer(adc, 0x48 + adcchan); // Indcates comm register to read data channel data register
      statusbyte = SPI.transfer(adc, 0); // Reads Channel 'ch' status
      db1 = SPI.transfer(adc, 0);        // Reads first byte
      db2 = SPI.transfer(adc, 0);        // Reads second byte
      ovr = statusbyte & 1;
      if (ovr) {
        break;
      }
      int decimal = twoByteToInt(db1, db2);
      float voltage = map2(decimal, 0, 65536, -10.0, 10.0);
      sum += voltage;
    }
    if (ovr)
    {
      *o1 = 128;
      *o2 = 0;
    }
    else
    {
      avg = sum / nReadings;
      int decimal = map2(avg, -10.0, 10.0, 0, 65536);
      intToTwoByte(decimal, &db1, &db2);
      *o1 = db1;
      *o2 = db2;
    }
  }
}

void rampRead(byte DB, byte b1, byte b2, byte * o1, byte * o2, int count, int nReadings )
{
  int adcChannel = DB;
  switch (adcChannel)
  {
    case 0:
      readingRampAvg(1, b1 , b2, o1, o2, count, nReadings);
      break;
    case 1:
      readingRampAvg(3, b1 , b2, o1, o2, count, nReadings);
      break;
    case 2:
      readingRampAvg(0, b1 , b2, o1, o2, count, nReadings);
      break;
    case 3:
      readingRampAvg(2, b1 , b2, o1, o2, count, nReadings);
      break;

    default:
      break;
  }
}

void bufferRamp(std::vector<String> DB)
{
  String channelsDAC = DB[1];
  int NchannelsDAC = channelsDAC.length();
  String channelsADC = DB[2];
  int NchannelsADC = channelsADC.length();
  std::vector<float> vi;
  std::vector<float> vf;
  float v_min = -10.0;
  float v_max = 10.0;
  for (int i = 3; i < NchannelsDAC + 3; i++)
  {
    vi.push_back(DB[i].toFloat());
    vf.push_back(DB[i + NchannelsDAC].toFloat());
  }
  int nSteps = (DB[NchannelsDAC * 2 + 3].toInt());
  byte b1;
  byte b2;
  int count = 0;
  for (int j = 0; j < nSteps; j++)
  {
    digitalWrite(data, HIGH);
    for (int i = 0; i < NchannelsDAC; i++)
    {
      float v = vi[i] + (vf[i] - vi[i]) * j / (nSteps - 1);
      if (v < v_min)
      {
        v = v_min;
      }
      else if (v > v_max)
      {
        v = v_max;
      }
      writeDAC(channelsDAC[i] - '0', v);
    }
    delayMicroseconds(DB[NchannelsDAC * 2 + 4].toInt());
    for (int i = 0; i < NchannelsADC; i++)
    {
      rampRead(channelsADC[i] - '0', b1, b2, &b1, &b2, count, DB[NchannelsDAC * 2 + 5].toInt());
      count += 1;
    }
  }
  Serial.write(b1);
  Serial.write(b2);
  digitalWrite(data, LOW);
}


void autoRamp1(std::vector<String> DB)
{
  float v1 = DB[2].toFloat();
  float v2 = DB[3].toFloat();
  int nSteps = DB[4].toInt();
  int dacChannel = DB[1].toInt();

  for (int j = 0; j < nSteps; j++)
  {
    int timer = micros();
    digitalWrite(data, HIGH);
    writeDAC(dacChannel, v1 + (v2 - v1)*j / (nSteps - 1));
    digitalWrite(data, LOW);
    while (micros() <= timer + DB[5].toInt());
  }
}

void autoRamp2(std::vector<String> DB)
{
  float vi1 = DB[3].toFloat();
  float vi2 = DB[4].toFloat();
  float vf1 = DB[5].toFloat();
  float vf2 = DB[6].toFloat();
  int nSteps = DB[7].toInt();
  byte b1;
  byte b2;
  int dacChannel1 = DB[1].toInt();
  int dacChannel2 = DB[2].toInt();

  for (int j = 0; j < nSteps; j++)
  {
    int timer = micros();
    digitalWrite(data, HIGH);
    writeDAC(dacChannel1, vi1 + (vf1 - vi1)*j / (nSteps - 1));
    writeDAC(dacChannel2, vi2 + (vf2 - vi2)*j / (nSteps - 1));
    while (micros() <= timer + DB[8].toInt());
    digitalWrite(data, LOW);
  }
}

//void autoRamp(std::vector<byte> DB)
//{
//  int v1=twoByteToVoltage(DB[1],DB[2]);
//  int v2=twoByteToVoltage(DB[3],DB[4]);
//  int nSteps=(DB[5]);
//  byte b1;
//  byte b2;
//  int dacChannel=(DB[0])&7;
//
//  for (int j=0; j<nSteps;j++)
//  {
//    digitalWrite(led,LOW);
//    voltageToTwoByte(v1+(v2-v1)*j/(nSteps-1), &b1, &b2);
//    dacDataSend(dacChannel,b1,b2);
//    delayMicroseconds(50);
//    readADC(DB[0]);
//    digitalWrite(led,HIGH);
//  }
//  digitalWrite(led,LOW);
//}


void dacDataReceive(int ch)
{
  Serial.flush();
  byte o2;
  byte o3;

  // Enables DAC-SDO
  SPI.transfer(dac, 1, SPI_CONTINUE);
  SPI.transfer(dac, 0, SPI_CONTINUE);
  SPI.transfer(dac, 0);

  SPI.transfer(dac, 144 + ch, SPI_CONTINUE); // Indicates to DAC to read channel 'ch' from the data register
  SPI.transfer(dac, 0, SPI_CONTINUE);     // Don't care
  SPI.transfer(dac, 0, SPI_LAST);         // Don't care
  SPI.transfer(dac, 0, SPI_CONTINUE);
  o2 = SPI.transfer(dac, 0, SPI_CONTINUE); // Reads first byte
  o3 = SPI.transfer(dac, 0);              // Reads second byte

  Serial.write(o2);
  Serial.write(o3);

  //Disables DAC-SDO
  SPI.transfer(dac, 1, SPI_CONTINUE);
  SPI.transfer(dac, 0, SPI_CONTINUE);
  SPI.transfer(dac, 1);
}

void readDAC(std::vector<String> DB)
{
  int dacChannel = DB[1].toInt();
  dacDataReceive(dacChannel);
}

void ID()
{
  Serial.println("DAC-ADC_AD7734-AD5764");
}

void RDY()
{
  Serial.println("READY");
}

void debug()
{
  digitalWrite(data, HIGH);
  delay(3000);
  digitalWrite(data, LOW);
  delay(3000);
}

//CUSTOM FUNCTIONS//////////////////////////////////////////////////////////////////////////
int fixMapADC(int adcChannel)
{
  switch (adcChannel)
  {
    case 0:
      return 1;
      break;
    case 1:
      return 3;
      break;
    case 2:
      return 0;
      break;
    case 3:
      return 2;
      break;
    default:
      return 0;
      break;
  }
}

//Copy of autoRamp1 while reading from ADC channel. Two serial term syntaxes based on selected nCh
//RAR1,[ADC#],[DAC#],[InitV],[FinalV],[Steps],[Delay]
//RARA,[InitV0],[FinalV0],[InitV1],[FinalV1],[InitV2],[FinalV2],[InitV3],[FinalV3],[Steps],[Delay]
//Example: RAR,0,0,0,5,-5,5,5,5,10,1000
//         Reads from ADCs 0,1, 2, and 3
//         while
//         ramping DACs 0,1,2,3 from 0 to 0v, 0 to 5v ,-5 to 5v, and 5v to 5v.
//         respectfully in 10 steps with 1000us delay
//         note: keep channels constant by giving the same value for init and final voltages.
//         --->Voltages are read out in 4, comma separated lines (ch0 to ch3 order)
void RAR(std::vector<String> DB,int nCh)
{
  //Read from ADC
  if(nCh == 1)
  {
    //Converting serial string into variables:
    float v1 = DB[3].toFloat();
    float v2 = DB[4].toFloat();
    int nSteps = DB[5].toInt();
    int dacChannel = DB[2].toInt();
    int adcChannel = fixMapADC(DB[1].toInt());

    //Ramp through values and save into buffer
    for (int j = 0; j < nSteps; j++)
    {
      int timer = micros();
      digitalWrite(data, HIGH);
      writeDAC(dacChannel, v1 + (v2 - v1)*j / (nSteps - 1));
      digitalWrite(data, LOW);
      linearWriteToBuffer(bufferv,j,getSingleReading(adcChannel));
      //while (micros() <= timer + (DB[6].toInt())/2); //wait half delay
      //read voltage from ADC
      while (micros() <= timer + DB[6].toInt());
    }
  }
  else
  {
    //Converting serial string into variables:
    float vi[4];
    float vf[4];
    int nSteps = DB[9].toInt();
    int StepDelay = DB[10].toInt();
    vi[0] = DB[1].toFloat();
    vf[0] = DB[2].toFloat();
    vi[1] = DB[3].toFloat();
    vf[1] = DB[4].toFloat();
    vi[2] = DB[5].toFloat();
    vf[2] = DB[6].toFloat();
    vi[3] = DB[7].toFloat();
    vf[3] = DB[8].toFloat();

    //Ramp through values and save into buffer
    for (int j = 0; j < nSteps; j++)
    {
      int timer = micros();
      digitalWrite(data, HIGH);
      writeDAC(0, vi[0] + (vf[0] - vi[0])*j / (nSteps - 1));
      writeDAC(1, vi[1] + (vf[1] - vi[1])*j / (nSteps - 1));
      writeDAC(2, vi[2] + (vf[2] - vi[2])*j / (nSteps - 1));
      writeDAC(3, vi[3] + (vf[3] - vi[3])*j / (nSteps - 1));
      digitalWrite(data, LOW);
      quadWriteToBuffer(bufferv,j,getSingleReading(fixMapADC(0)), getSingleReading(fixMapADC(1)), getSingleReading(fixMapADC(2)), getSingleReading(fixMapADC(3)));
      //while (micros() <= timer + (DB[6].toInt())/2); //wait half delay
      //read voltage from ADC
      while (micros() <= timer + StepDelay);
    }
  }

  //Read out buffer:
  if(nCh == 1)
  {
    linearReadBuffer(bufferv,DB[5].toInt());
  }
  else
  {
    quadReadBuffer(bufferv,DB[9].toInt());
  }

  //Clear buffer:
  clearbuffer(bufferv);
}

//Acquire over time nSamples with time sampleStep(s) between each sample
//Two Serial term syntaxes based on selection of 1 ch or quad acquire
//Syntax: ACQ1,ADC#,nSamples,sampleStep
//Syntax: ACQ4,nSamples,sampleStep
void ACQ(std::vector<String> DB,int nCh)
{
  int nSamplesToRead = 0;
//Read from ADC
  if(nCh == 1)
  {
    //Syntax: ACQ1,ADC#,nSamples,sampleStep
    //Converting serial string into variables:
    int adcChannel = fixMapADC(DB[1].toInt());
    int nSamples = DB[2].toInt(); // Input seconds but internally microsec
    float sampleStep = DB[3].toFloat()*1000000.0; //Time between each sample (1/f) (input: seconds)

    //Since 1 channel, can have bufferv_xdim*bufferv_ydim samples! Check.
    if (nSamples>(bufferv_xdim*bufferv_ydim))
    {
      nSamples = bufferv_xdim*bufferv_ydim;
    }
    nSamplesToRead = nSamples;
    
    //Ramp through values and save into buffer
    for (int j = 0; j < nSamples; j++)
    {
      int timer = micros();
      linearWriteToBuffer(bufferv,j,getSingleReading(adcChannel));
      while (micros() <= timer + sampleStep);
    }
  }
  else if (nCh == 2)
  {
    //Syntax: ACQ1,ADC_A#,ADC_B#,nSamples,sampleStep
    //Converting serial string into variables:
    int adcChannelA = fixMapADC(DB[1].toInt());
    int adcChannelB = fixMapADC(DB[2].toInt());
    int nSamples = DB[3].toInt(); // Input seconds but internally microsec
    float sampleStep = DB[4].toFloat()*1000000.0; //Time between each sample (1/f) (input: seconds)

    //Since 1 channel, can have bufferv_xdim*bufferv_ydim samples! Check.
    if (nSamples>(bufferv_xdim*bufferv_ydim))
    {
      nSamples = bufferv_xdim*bufferv_ydim;
    }
    nSamplesToRead = nSamples;
    
    //Ramp through values and save into buffer
    for (int j = 0; j < nSamples; j++)
    {
      int timer = micros();
      linearWriteToBuffer(bufferv,j,getSingleReading(adcChannel));
      while (micros() <= timer + sampleStep);
    }
  }
  
  else
  {
    //Syntax: ACQ4,nSamples,sampleStep
    //Converting serial string into variables:
    int nSamples = DB[1].toInt(); // Input seconds but internally microsec
    float sampleStep = DB[2].toFloat()*1000000.0; //Time between each sample (1/f) (input: seconds)

    //Since 4 channels, can havebufferv_ydim samples! Check and Correct
    if (nSamples>(bufferv_ydim))
    {
      nSamples = bufferv_ydim;
    }
    nSamplesToRead = nSamples;
    
    //Read from ADC
    for (int j = 0; j < nSamples; j++)
    {
      int timer = micros();
      quadWriteToBuffer(bufferv,j,getSingleReading(fixMapADC(0)), getSingleReading(fixMapADC(1)), getSingleReading(fixMapADC(2)), getSingleReading(fixMapADC(3)));
      while (micros() <= timer + sampleStep);
    }
  }

  //Read out buffer:
  if(nCh == 1)
  {
    linearReadBuffer(bufferv,nSamplesToRead);
  }
  else
  {
    quadReadBuffer(bufferv,nSamplesToRead);
  }

  //Clear buffer:
  clearbuffer(bufferv);



  //Make sure to ensure that IntTime < Samplerate ** -1 !!!!!!!!


}

//Sine Wave out
//Syntax: SIN,DAC#,V0,ANGFREQ(rads/sec),PHASE(radians),OFFSET,duration(ms)
void sinw(std::vector<String> DB)
{
  int dacChannel = DB[1].toInt();
  float v0 = DB[2].toFloat();
  float w = DB[3].toFloat();
  float phi = DB[4].toFloat();
  float vdc = DB[5].toFloat();
  float interval = DB[6].toFloat();
  /*
  for (int j = 0; j < nSteps; j++)
  {
    float timer = micros();
    digitalWrite(data, HIGH);
    writeDAC(dacChannel, vdc + v0 * sin(((w * interval * j) / 1000.0) + phi));
    writeDAC(dacChannel, vdc + v0 * sin(((w * timer) / 1000.0) + phi));
    digitalWrite(data, LOW);
    while (micros() <= timer + interval);
  }
  */
  float timer0 = micros(); //Time at start of wave
  while((micros() - timer0) <= interval*1000.0) // run only when wave ran for the requested interval
  {
    digitalWrite(data, HIGH);
    writeDAC(dacChannel, vdc + v0 * sin(w * ((micros()-timer0)/ 1000000.0) + phi));
    digitalWrite(data, LOW);
  }
}
//Sine Wave out
//Syntax: SIN,DAC#,V0,ANGFREQ(rads/sec),PHASE(radians),OFFSET,duration(ms)
void sinw4(std::vector<String> DB)
{
  float v00 = DB[1].toFloat();
  float v01 = DB[2].toFloat();
  float v02 = DB[3].toFloat();
  float v03 = DB[4].toFloat();
  float w0 = DB[5].toFloat();
  float w1 = DB[6].toFloat();
  float w2 = DB[7].toFloat();
  float w3 = DB[8].toFloat();
  float phi0 = DB[9].toFloat();
  float phi1 = DB[10].toFloat();
  float phi2 = DB[11].toFloat();
  float phi3 = DB[12].toFloat();
  float vdc0 = DB[13].toFloat();
  float vdc1 = DB[14].toFloat();
  float vdc2 = DB[15].toFloat();
  float vdc3 = DB[16].toFloat();
  float interval = DB[17].toFloat();

  //Suggest to use pre-computed table for sine waves to avoid the phase delays(120us)
  float timer0 = micros(); //Time at start of wave
  while((micros() - timer0) <= interval*1000.0) // run only when wave ran for the requested interval
  {
    digitalWrite(data, HIGH);
    writeDAC(0, vdc0 + v00 * sin(w0 * ((micros()-timer0)/ 1000000.0) + phi0));
    writeDAC(1, vdc1 + v01 * sin(w1 * ((micros()-timer0-120)/ 1000000.0) + phi1)); //-120us attempt to fix phase offset. Unsuccessful. Left as note
    writeDAC(2, vdc2 + v02 * sin(w2 * ((micros()-timer0-240)/ 1000000.0) + phi2));
    writeDAC(3, vdc3 + v03 * sin(w2 * ((micros()-timer0-360)/ 1000000.0) + phi3));
    digitalWrite(data, LOW);
  }
}
/*
void SRAMF(std::vector<String> DB)
{
  Serial.println(String(freeMemory()));
}
*/

  void router(std::vector<String> DB)
  {
  float v;
  int operation = indexOfOperation(DB[0]);
  switch ( operation )
  {
    case 0:
      Serial.println("NOP");
      break;

    case 1: // Write DAC **IMPLEMENTED, WORKS
      if (DB[2].toFloat() < -10 || DB[2].toFloat() > 10)
      {
        Serial.println("VOLTAGE_OVERRANGE");
        break;
      }
      v = writeDAC(DB[1].toInt(), DB[2].toFloat());
      Serial.print("DAC ");
      Serial.print(DB[1]);
      Serial.print(" UPDATED TO ");
      Serial.print(v, 4);
      Serial.println("V");
      break;

    case 2: // Read ADC
      v = readADC(DB[1].toInt());
      Serial.println(v, 6);
      break;

    //    case 3: // not working with current shield
    //    readDAC(DB);
    //    break;

    case 3:
      autoRamp1(DB);
      Serial.println("RAMP_FINISHED");
      break;

    case 4:
      autoRamp2(DB);
      Serial.println("RAMP_FINISHED");
      break;

    case 5: // Autoramp
      bufferRamp(DB);
      Serial.println("BUFFER_RAMP_FINISHED");
      break;

    case 6:
      resetADC();
      break;

    case 7:
      talkADC(DB);
      break;

    case 8: // Write conversion time registers
      writeADCConversionTime(DB);
      break;

    case 9: // ID
      ID();
      break;

    case 10:
      RDY();
      break;

    case 11: //Ramp and Read 1 ch
      RAR(DB,1);
      //Serial.println("RAMP_AND_READ_FINISHED");
      break;

    case 12: // Sine Output
      sinw(DB);
      Serial.println("SINE_FINISHED");
      break;

     case 13: // Acquire over time, all channels
       ACQ(DB,4);
       break;

     case 14: // Ramp and Read over time, all channels
       RAR(DB,4);
       break;
     case 15: // Print Free SRAM
       //SRAMF(DB);
       break;
     case 16: //Acquire 1 ch
       ACQ(DB,1);
       break;
     case 17:
       sinw4(DB);
       break;

    default:
      break;
  }
  }




//bool commandsout = 1;
void loop()
{
  Serial.flush();
  String inByte = "";
  std::vector<String> comm;
  if (Serial.available())
  {
    char received;
    while (received != '\r')
    {
      if (Serial.available())
      {
        received = Serial.read();
        if (received == '\n' || received == ' ')
        {}
        else if (received == ',' || received == '\r')
        {
          comm.push_back(inByte);
          inByte = "";
        }
        else
        {
          inByte += received;
        }
      }
    }
    router(comm);
  }
}
