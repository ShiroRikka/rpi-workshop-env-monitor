import time
import board
import adafruit_dht

class rsi_dht11:
    def __init__(self,pin=board.D14):
        self.pin = pin
        self.sersor = adafruit_dht.DHT11(self.pin)

    def read(self):
        try:
            temperature = self.sersor.temperature
            humidity = self.sersor.humidity
            
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
            
if __name__ == "__main__":
    dht11 = rsi_dht11(board.D14)
    while True:
        dht11.read()
        time.sleep(2)
