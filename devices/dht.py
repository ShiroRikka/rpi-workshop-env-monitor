import time
import board
import adafruit_dht

# 初始化DHT11传感器
dht11 = adafruit_dht.DHT11(board.D14)

def read_dht11_circuitpython():
    """使用CircuitPython库读取DHT11"""
    try:
        temperature = dht11.temperature
        humidity = dht11.humidity
        
        if temperature is not None and humidity is not None:
            print(f"温度: {temperature:.1f}°C")
            print(f"湿度: {humidity:.1f}%")
            return temperature, humidity
        else:
            print("读取失败")
            return None, None
            
    except RuntimeError as e:
        # DHT传感器读取可能偶尔失败，这是正常的
        print(f"读取错误: {e.args[0]}")
        return None, None
    except Exception as e:
        print(f"其他错误: {e}")
        return None, None

# 主程序
if __name__ == "__main__":
    while True:
        read_dht11_circuitpython()
        time.sleep(2)
