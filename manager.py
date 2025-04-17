import asyncio
from serial import Serial, SerialException


class Ports:
    def __init__(self, port_name, baud_rate):
        try:
            self.ser = Serial(port_name, baud_rate, timeout=1)
        except SerialException as e:
            print(f"Ошибка при открытии порта {port_name}: {e}")
            raise

    async def clear_buffer(self):
        try:
            if self.ser.is_open:
                await asyncio.to_thread(self.ser.close)
            await asyncio.to_thread(self.ser.open)
            await asyncio.to_thread(self.ser.reset_input_buffer)
            await asyncio.to_thread(self.ser.reset_output_buffer)
            return True
        except SerialException as e:
            print(f"Ошибка при очистке буфера: {e}")
            return False

    async def _read_response(self):
        """
        Приватный метод для асинхронного чтения данных из последовательного порта.
        """
        response_lines = []
        try:
            while self.ser.in_waiting > 0:
                line = await asyncio.to_thread(self.ser.readline)
                line = line.decode().strip()
                if line and '-' in line:
                    response_lines.append(line)
        except SerialException as e:
            print(f"Ошибка при чтении из порта: {e}")
        return response_lines

    async def send_command(self, command):
        """
        Асинхронно отправляет команду и возвращает ответ, считанный с последовательного порта.
        """
        try:
            await asyncio.to_thread(self.ser.write, (command + '\n').encode())
            await asyncio.sleep(3)
            return await self._read_response()
        except SerialException as e:
            print(f"Ошибка при отправке команды '{command}': {e}")
            return []

    async def read_commands(self):
        """
        Асинхронно считывает команды, используя общий метод _read_response.
        """
        return await self._read_response()
