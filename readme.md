# 树莓派环境监控系统

一个基于树莓派的车间环境监控系统，能够实时监测温度、湿度和烟雾水平，并根据温度自动控制风扇转速。

## 功能特性

- **多传感器监测**：支持DHT11温湿度传感器、DS18B20温度传感器和MQ2烟雾传感器
- **智能风扇控制**：根据温度自动调节风扇转速，实现温度自适应控制
- **温度报警系统**：当温度超过阈值时自动触发警报器，支持常亮和闪烁模式
- **实时数据显示**：通过LCD1602显示屏实时显示环境数据
- **数据记录**：将传感器数据保存到SQLite数据库，支持历史数据查询
- **Web API接口**：提供RESTful API，支持远程监控和数据获取
- **异步架构**：基于Python asyncio的高性能异步架构

## 系统架构

```
树莓派环境监控系统
├── 硬件层
│   ├── 传感器模块
│   │   ├── DHT11温湿度传感器
│   │   ├── DS18B20温度传感器
│   │   └── MQ2烟雾传感器
│   └── 执行器模块
│       ├── 直流电机（风扇控制）
│       └── 警报器（温度报警）
├── 服务层
│   ├── 数据管理服务（数据采集与控制）
│   └── 显示管理服务（LCD显示）
├── API层
│   └── FastAPI Web服务
└── 数据层
    └── SQLite数据库
```

## 硬件连接指南

### DHT11温湿度传感器

DHT11传感器有三个引脚，连接方式如下：

- **负极（GND）**：连接到树莓派的GND引脚
- **正极（VCC）**：连接到树莓派的3.3V
- **信号引脚（DATA）**：连接到树莓派的GPIO24（可通过配置修改）

> **注意**：请根据DHT11模块上的标识确定负极引脚，通常会有"-"或"GND"标识。

### DS18B20温度传感器

DS18B20是单总线数字温度传感器：

- **VCC**：连接到5V
- **GND**：连接到GND
- **DATA**：连接到GPIO4（树莓派默认单总线引脚）

### MQ2烟雾传感器

MQ2传感器需要通过ADC读取模拟值：

- **VCC**：连接到5V
- **GND**：连接到GND
- **AOUT**：连接到MCP3008 ADC的通道0（AIN0）

#### MCP3008 ADC模块连接

- **VCC**：连接到3.3V
- **GND**：连接到GND
- **CLK**：连接到GPIO11（CLK）
- **MOSI**：连接到GPIO10（MOSI）
- **MISO**：连接到GPIO9（MISO）
- **CS**：连接到GPIO8（CE0）

### LCD1602显示屏

LCD1602通过I2C接口连接：

- **VCC**：连接到5V
- **GND**：连接到GND
- **SDA**：连接到GPIO2（SDA）
- **SCL**：连接到GPIO3（SCL）

### 直流电机（风扇）

使用L298N电机驱动模块控制直流电机：

- **L298N与树莓派连接**：
  - IN1 → GPIO17
  - IN2 → GPIO18
  - ENA → GPIO19（PWM控制）
  - 5V → 树莓派5V（电源）
  - GND → 树莓派GND（共地）

### 警报器（Warning）

使用继电器模块控制警报器：

- **继电器模块与树莓派连接**：
  - VCC → 树莓派5V（电源）
  - GND → 树莓派GND（共地）
  - IN → GPIO22（控制信号）

- **警报器与继电器连接**：
  - 警报器正极 → 继电器常开（NO）端口
  - 警报器负极 → 继电器公共（COM）端口
  - 外部电源正极 → 继电器公共（COM）端口（如果警报器需要独立供电）
  - 外部电源负极 → 警报器负极（如果警报器需要独立供电）

> **注意**：警报器可以配置为常亮模式或闪烁模式，通过配置文件中的 `WARNING_BLINK_ENABLED` 参数控制。

## 安装与配置

### 环境要求

- Python 3.11+
- 树莓派OS（推荐使用最新版）
- 管理员权限（用于GPIO访问）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd rpi-workshop-env-monitor
   ```

2. **安装依赖**
   ```bash
   # 使用uv（推荐）
   uv sync
   ```

3. **启用树莓派I2C和GPIO**
   ```bash
   sudo raspi-config
   # 选择 "Interfacing Options" → "I2C" → "Enable"
   # 选择 "Interfacing Options" → "SPI" → "Enable"（如果使用SPI ADC）
   ```

4. **配置系统权限**
   ```bash
   # 将用户添加到gpio组
   sudo usermod -a -G gpio $USER
   
   # 重新登录或重启使权限生效
   ```

### 配置说明

系统配置通过[`config.py`](config.py:1)文件和环境变量进行管理。主要配置项：

#### API配置
```python
API_HOST: str = "0.0.0.0"  # API服务监听地址
API_PORT: int = 8000        # API服务端口
```

#### 数据采集配置
```python
DATA_COLLECTION_INTERVAL: int = 3    # 数据采集间隔（秒）
DISPLAY_UPDATE_INTERVAL: int = 3     # 显示更新间隔（秒）
```

#### LCD显示器配置
```python
LCD_ADDRESS: int = 0x27      # I2C地址
LCD_BUS_NUM: int = 1        # I2C总线编号
LCD_COLS: int = 16          # LCD列数
LCD_ROWS: int = 2           # LCD行数
```

#### 硬件引脚配置
```python
DHT11_PIN: board.pin = board.D24           # DHT11信号引脚
FAN_MOTOR_FORWARD: int = 17                # 风扇正转引脚
FAN_MOTOR_BACKWARD: int = 18               # 风扇反转引脚
FAN_MOTOR_ENABLE: int = 19                 # 风扇使能引脚（PWM）
SMOKE_SENSOR_ADC_CHANNEL: int = 0          # 烟雾传感器ADC通道
WARNING_PIN: int = 22                      # 警报器控制引脚
```

#### 控制逻辑阈值
```python
SMOKE_THRESHOLD: float = 600.0             # 烟雾报警阈值
TEMPERATURE_THRESHOLD: float = 22.0        # 温度报警阈值

# 风扇变速控制参数
FAN_MIN_TEMP: float = 20.0                 # 风扇启动温度
FAN_MAX_TEMP: float = 35.0                 # 风扇全速温度
FAN_MIN_SPEED: float = 0.1                 # 最低转速比例
FAN_MAX_SPEED: float = 1.0                 # 最高转速比例
```

#### 警报器配置
```python
WARNING_BLINK_ENABLED: bool = True         # 是否启用闪烁模式
WARNING_BLINK_INTERVAL: float = 0.5        # 闪烁间隔（秒）
WARNING_BLINK_DUTY_CYCLE: float = 0.5      # 闪烁占空比（0.0-1.0），1.0表示常亮
```

警报器控制逻辑在[`services/data_manager.py`](services/data_manager.py:169)中的[`_control_warning()`](services/data_manager.py:169)方法实现，硬件控制在[`hardware/actuators.py`](hardware/actuators.py:7)中的[`RpiRelay`](hardware/actuators.py:7)类实现。

#### 数据库配置
```python
DATABASE_URL: str = "./data.db"            # SQLite数据库文件路径
```

#### 日志配置
```python
LOG_LEVEL: str = "INFO"                    # 日志级别
LOG_PATH: any = sys.stderr                 # 日志输出路径
```

### 环境变量配置

可以通过创建`.env`文件来覆盖默认配置：

```bash
# .env 文件示例
API_HOST=192.168.1.100
API_PORT=8080
DATA_COLLECTION_INTERVAL=5
LOG_LEVEL=DEBUG
DATABASE_URL=/path/to/database.db
WARNING_PIN=22
WARNING_BLINK_ENABLED=true
WARNING_BLINK_INTERVAL=0.5
WARNING_BLINK_DUTY_CYCLE=0.5
```

## 使用方法

### 启动系统

```bash
python main.py
```

系统启动后会自动：
1. 初始化所有传感器和执行器
2. 创建数据库表（如果不存在）
3. 启动数据采集循环
4. 启动LCD显示更新
5. 启动Web API服务

### 查看实时数据

系统启动后，可以通过以下方式查看数据：

1. **LCD显示屏**：实时显示温度、湿度、烟雾水平、风扇状态和警报状态
2. **Web API**：访问 `http://树莓派IP:8000` 获取JSON格式数据

### API使用说明

系统提供以下API端点：

#### 获取欢迎信息
```http
GET /
```

响应示例：
```json
{
  "message": "欢迎使用树莓派监控API"
}
```

#### 获取当前状态
```http
GET /status
```

响应示例：
```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "smoke_level": 450.3,
  "fan_on": true,
  "fan_speed": 0.45,
  "warning_on": false
}
```

#### 获取历史数据
```http
GET /history?limit=100
```

参数：
- `limit`：返回记录数量（默认100，最大1000）

响应示例：
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-01T12:00:00",
    "temperature": 23.5,
    "humidity": 65.2,
    "smoke_level": 450.3,
    "fan_on": true,
    "fan_speed": 0.45,
    "warning_on": false
  },
  ...
]
```

### 风扇控制逻辑

系统根据温度自动控制风扇转速：

1. **温度 ≤ FAN_MIN_TEMP（20.0°C）**：风扇关闭
2. **FAN_MIN_TEMP < 温度 < FAN_MAX_TEMP（35.0°C）**：线性调节转速
3. **温度 ≥ FAN_MAX_TEMP**：风扇全速运转

转速计算公式：
```
转速比例 = (当前温度 - 最低温度) / (最高温度 - 最低温度)
实际转速 = 最低转速 + 转速比例 × (最高转速 - 最低转速)
```

### 警报器控制逻辑

系统根据温度自动控制警报器：

1. **温度 ≤ TEMPERATURE_THRESHOLD（22.0°C）**：警报器关闭
2. **温度 > TEMPERATURE_THRESHOLD**：警报器开启

警报器工作模式：
- **常亮模式**：当 `WARNING_BLINK_ENABLED = False` 时，警报器持续工作
- **闪烁模式**：当 `WARNING_BLINK_ENABLED = True` 时，警报器按照设定的间隔和占空比闪烁
  - 闪烁间隔由 `WARNING_BLINK_INTERVAL` 控制（默认0.5秒）
  - 闪烁占空比由 `WARNING_BLINK_DUTY_CYCLE` 控制（默认0.5，即50%时间开启）

## 故障排除

### 常见问题

#### 1. DHT11传感器读取失败

**症状**：日志显示DHT11读取错误或返回None

**解决方案**：
- 检查引脚连接是否正确
- 确认传感器供电正常（3.3V或5V）
- 在信号线和VCC之间添加10kΩ上拉电阻
- 尝试增加读取间隔（DHT11需要至少2秒间隔）

#### 2. LCD显示异常

**症状**：LCD无显示或显示乱码

**解决方案**：
- 检查I2C连接（SDA、SCL、VCC、GND）
- 确认I2C地址是否正确（使用`i2cdetect -y 1`扫描）
- 检查I2C是否已启用（`sudo raspi-config`）
- 尝试调整对比度（如果LCD有对比度调节电位器）

#### 3. 风扇不转动

**症状**：温度超过阈值但风扇不转动

**解决方案**：
- 检查电机驱动模块供电
- 确认GPIO引脚连接正确
- 检查电机驱动模块与树莓派共地
- 使用万用表测试电机驱动模块输出

#### 4. API无法访问

**症状**：浏览器无法访问Web界面

**解决方案**：
- 检查防火墙设置
- 确认API_HOST配置（0.0.0.0允许外部访问）
- 检查端口是否被占用
- 查看日志确认API服务是否正常启动

#### 5. 警报器不工作

**症状**：温度超过阈值但警报器不响

**解决方案**：
- 检查继电器模块连接（VCC、GND、IN引脚）
- 确认GPIO22引脚连接正确
- 检查继电器模块供电是否正常
- 测试继电器模块是否正常工作（使用万用表）
- 确认警报器本身是否正常（直接连接电源测试）
- 检查配置文件中的WARNING_PIN设置是否正确

#### 6. 数据库错误

**症状**：启动时数据库初始化失败

**解决方案**：
- 检查数据库文件路径权限
- 确认磁盘空间充足
- 删除现有数据库文件重新初始化
- 检查SQLite是否正确安装

### 调试模式

启用详细日志以便调试：

1. **修改日志级别**
   ```python
   LOG_LEVEL: str = "DEBUG"
   ```

2. **查看实时日志**
   ```bash
   tail -f logs/app.log
   ```

3. **测试单个组件**
   ```python
   # 测试DHT11传感器
   from hardware.dht11_sensor import DHT11Sensor
   import board
   
   sensor = DHT11Sensor(board.D24, "humid")
   print(sensor.read())
   ```

### 性能优化

1. **减少数据采集频率**
   ```python
   DATA_COLLECTION_INTERVAL: int = 10  # 增加到10秒
   ```

2. **优化数据库写入**
   - 考虑批量写入而非单条写入
   - 定期清理旧数据

3. **减少LCD更新频率**
   ```python
   DISPLAY_UPDATE_INTERVAL: int = 5  # 增加到5秒
   ```

## 开发指南

### 项目结构

```
rpi-workshop-env-monitor/
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── state.py               # 共享状态
├── api/                   # API模块
│   ├── __init__.py
│   └── main_api.py        # FastAPI服务
├── database/              # 数据库模块
│   ├── __init__.py
│   └── db.py              # 数据库操作
├── hardware/              # 硬件抽象层
│   ├── __init__.py
│   ├── base_sensor.py     # 传感器基类
│   ├── base_actuator.py   # 执行器基类
│   ├── dht11_sensor.py    # DHT11传感器
│   ├── ds18b20_sensor.py  # DS18B20传感器
│   ├── mq2_sensor.py      # MQ2传感器
│   └── actuators.py       # 执行器实现（包含警报器控制）
└── services/              # 服务层
    ├── __init__.py
    ├── base_manager.py    # 管理器基类
    ├── data_manager.py    # 数据管理服务（包含警报器控制逻辑）
    ├── display_manager.py # 显示管理服务
    └── lcd1602.py         # LCD驱动
```

### 添加新传感器

1. **创建传感器类**
   ```python
   # hardware/new_sensor.py
   from .base_sensor import BaseSensor
   
   class NewSensor(BaseSensor):
       def __init__(self, pin):
           super().__init__()
           self.pin = pin
           
       async def read(self):
           # 实现读取逻辑
           pass
   ```

2. **注册到数据管理器**
   ```python
   # services/data_manager.py
   def _initialize_sensors(self):
       return {
           "dht11": DHT11Sensor(...),
           "new_sensor": NewSensor(...),
       }
   ```

3. **更新配置**
   ```python
   # config.py
   NEW_SENSOR_PIN: board.pin = board.D25
   ```

### 扩展API

在[`api/main_api.py`](api/main_api.py:1)中添加新端点：

```python
@app.get("/custom_endpoint")
async def custom_endpoint():
    # 实现自定义逻辑
    return {"data": "custom_data"}
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue

---

**注意**：本系统设计用于车间环境监控，请根据实际需求调整阈值和配置参数。
