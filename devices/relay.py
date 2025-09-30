from gpiozero import OutputDevice
import time

# 使用示例
if __name__ == "__main__":
    relay = OutputDevice(14,initial_value=False)
    relay.on()
    time.sleep(2)
    relay.close()

