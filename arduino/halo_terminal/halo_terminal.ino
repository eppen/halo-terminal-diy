// Arduino Halo Terminal
// 引脚定义（可根据需要调整）
#define PIN_RED 9
#define PIN_GREEN 10
#define PIN_BLUE 11
// 亮度电位器：模拟输入 A0（外侧接 5V / GND，中间接 A0）
#define PIN_BRIGHTNESS A0

// 状态颜色定义
enum State {
  STATE_IDLE,      // 蓝色 - 空闲，等待输入
  STATE_THINKING,  // 黄色 - 正在处理
  STATE_INPUT,     // 红色 - 需要输入
  STATE_ERROR      // 紫色 - 错误
};

State currentState = STATE_IDLE;

// 逻辑 RGB（0–255），实际 PWM 会再乘以亮度系数
uint8_t logicalR = 0;
uint8_t logicalG = 0;
uint8_t logicalB = 0;
// 电位器映射后的亮度 0–255（0 为熄灭，255 为最亮）
uint8_t brightness = 255;

void setup() {
  Serial.begin(9600);
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE, OUTPUT);
  // A0 默认即为模拟输入，无需 pinMode

  setColor(0, 0, 255);  // 启动时显示蓝色
  delay(500);
  setColor(0, 255, 0);  // 绿色
  delay(500);
  setColor(255, 0, 0);  // 红色
  delay(500);
  setColor(0, 0, 255);  // 返回蓝色

  readBrightnessPot();  // 与电位器初始位置对齐

  Serial.println("Halo Terminal Ready!");
}

void loop() {
  readBrightnessPot();

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("Received: ");
    Serial.println(command);

    if (command == "idle") {
      setState(STATE_IDLE);
    } else if (command == "thinking") {
      setState(STATE_THINKING);
    } else if (command == "input") {
      setState(STATE_INPUT);
    } else if (command == "error") {
      setState(STATE_ERROR);
    } else if (command.startsWith("rgb:")) {
      // 自定义颜色，格式: rgb:255,0,0
      parseRGB(command);
    } else if (command == "breathing") {
      breathingEffect(0, 0, 255);  // 蓝色呼吸灯
    } else if (command == "test") {
      runTestSequence();
    }
  }

  // 空闲时可根据状态添加呼吸效果
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 1000) {
    lastBlink = millis();
    if (currentState == STATE_INPUT) {
      // 需要输入时闪烁红色
      static bool blinkState = false;
      blinkState = !blinkState;
      if (blinkState) {
        setColor(255, 0, 0);
      } else {
        setColor(0, 0, 0);
      }
    }
  }
}

void setState(State state) {
  currentState = state;
  switch(state) {
    case STATE_IDLE:      // 蓝色
      setColor(0, 0, 255);
      break;
    case STATE_THINKING:  // 黄色
      setColor(255, 255, 0);
      break;
    case STATE_INPUT:     // 红色
      setColor(255, 0, 0);
      break;
    case STATE_ERROR:     // 紫色
      setColor(255, 0, 255);
      break;
  }
}

void parseRGB(String command) {
  // 解析 rgb:255,0,0 格式
  int firstComma = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);

  if (firstComma > 0 && secondComma > 0) {
    int r = command.substring(4, firstComma).toInt();
    int g = command.substring(firstComma + 1, secondComma).toInt();
    int b = command.substring(secondComma + 1).toInt();

    setColor(r, g, b);
  }
}

// 根据 logical* 与 brightness 写出 PWM（共阳极）
void applyColorToPwm() {
  uint8_t r = (uint16_t)logicalR * brightness / 255;
  uint8_t g = (uint16_t)logicalG * brightness / 255;
  uint8_t b = (uint16_t)logicalB * brightness / 255;
  // 共阳极RGB LED：低电平点亮
  analogWrite(PIN_RED, 255 - r);
  analogWrite(PIN_GREEN, 255 - g);
  analogWrite(PIN_BLUE, 255 - b);

  // 如果是共阴极RGB LED，使用下面的代码：
  // analogWrite(PIN_RED, r);
  // analogWrite(PIN_GREEN, g);
  // analogWrite(PIN_BLUE, b);
}

// 读取电位器并仅在亮度变化明显时刷新输出（减轻 ADC 抖动）
void readBrightnessPot() {
  int raw = analogRead(PIN_BRIGHTNESS);
  raw = constrain(raw, 0, 1023);
  uint8_t b = map(raw, 0, 1023, 0, 255);
  static uint8_t lastB = 255;
  if ((int)abs((int)b - (int)lastB) > 1) {
    lastB = b;
    brightness = b;
    applyColorToPwm();
  }
}

// 设置RGB颜色（0-255，为逻辑亮度；实际亮度由电位器整体缩放）
void setColor(int red, int green, int blue) {
  logicalR = constrain(red, 0, 255);
  logicalG = constrain(green, 0, 255);
  logicalB = constrain(blue, 0, 255);
  applyColorToPwm();
}

// 呼吸灯效果
void breathingEffect(int r, int g, int b) {
  for (int i = 0; i <= 255; i++) {
    setColor(r * i / 255, g * i / 255, b * i / 255);
    delay(10);
  }
  for (int i = 255; i >= 0; i--) {
    setColor(r * i / 255, g * i / 255, b * i / 255);
    delay(10);
  }
  setColor(r, g, b);
}

// 测试序列
void runTestSequence() {
  Serial.println("Running test sequence...");

  setColor(255, 0, 0);    // 红
  delay(500);
  setColor(0, 255, 0);    // 绿
  delay(500);
  setColor(0, 0, 255);    // 蓝
  delay(500);
  setColor(255, 255, 0);  // 黄
  delay(500);
  setColor(255, 0, 255);  // 紫
  delay(500);
  setColor(0, 255, 255);  // 青
  delay(500);

  breathingEffect(0, 255, 0);  // 绿色呼吸灯

  setColor(0, 0, 255);    // 返回蓝色（空闲状态）
  Serial.println("Test sequence complete!");
}