import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

# 注意：这些UUID是Bluetooth SIG为标准"Nordic UART Service"定义的
# 很多Micro:bit的BLE示例和使用MakeCode的Bluetooth扩展时会使用这个服务
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # 微比特收，电脑发
UART_TX_CHARACTERISTIC_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # 微比特发，电脑收

# 创建一个异步队列用于存放接收到的数据
received_data_queue = asyncio.Queue()


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """处理从micro:bit接收到的通知（数据）"""
    try:
        decoded_text = data.decode('utf-8')
        print(f"\n[来自 micro:bit] {decoded_text}", end='')
        # 如果需要将收到的数据用于其他地方，可以放入队列
        # asyncio.create_task(received_data_queue.put(decoded_text))
    except UnicodeDecodeError:
        print(f"\n[来自 micro:bit] (原始字节数据) {data.hex()}")


async def main():
    devices = await BleakScanner.discover()
    target_device = None
    for d in devices:
        # 寻找名称包含 'micro:bit' 的设备
        if d.name and 'micro:bit' in d.name.lower():
            print(f"找到设备: {d.name}, 地址: {d.address}")
            target_device = d
            break

    if target_device is None:
        print("未找到名称包含 'micro:bit' 的BLE设备。请确保:")
        print("1. micro:bit 已正确供电并程序运行中。")
        print("2. micro:bit 的蓝牙可见/可连接。")
        print("3. Windows 10 的蓝牙已打开并正常工作。")
        return

    async with BleakClient(target_device.address) as client:
        print(f"\n已连接到 {target_device.name}")

        # 确保所需的UART服务存在
        uart_service = client.services.get_service(UART_SERVICE_UUID)
        if uart_service is None:
            print(f"错误：在设备上未找到UUID为 {UART_SERVICE_UUID} 的UART服务。")
            print("请检查micro:bit端的程序是否正确配置了蓝牙UART服务。")
            await client.disconnect()
            return

        # 获取TX和RX特征值
        rx_char = uart_service.get_characteristic(UART_RX_CHARACTERISTIC_UUID)
        tx_char = uart_service.get_characteristic(UART_TX_CHARACTERISTIC_UUID)

        if rx_char is None or tx_char is None:
            print("错误：未找到UART RX或TX特征值。")
            await client.disconnect()
            return

        # 启动通知，订阅TX特征值（接收micro:bit发来的数据）
        await client.start_notify(tx_char.uuid, notification_handler)
        print("已开启通知，可以接收micro:bit发来的数据...")
        print("输入消息并按回车发送 (输入 'quit' 退出):")

        # 循环发送和接收数据
        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "")
                if user_input.lower() == 'quit':
                    break
                # 发送数据到micro:bit的RX特征值
                # 确保字符串以换行符结尾或符合micro:bit程序的预期格式
                data_to_send = (user_input + '\n').encode('utf-8')  # 添加换行符
                await client.write_gatt_char(rx_char.uuid, data_to_send)
                print(f"[消息已发送] {user_input}")
        except asyncio.CancelledError:
            pass
        finally:
            # 停止通知并断开连接
            await client.stop_notify(tx_char.uuid)
            print("\n已停止通知并断开连接。")


if __name__ == "__main__":
    asyncio.run(main())
