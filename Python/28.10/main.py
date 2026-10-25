import asyncio
from time import monotonic


# Общий механизм событий
class Events:
    def __init__(self):
        self.handlers = {}

    def on(self, event, handler):
        items = self.handlers.setdefault(event, [])
        if handler not in items:
            items.append(handler)

    def off(self, event, handler):
        items = self.handlers.get(event, [])
        if handler in items:
            items.remove(handler)

    def emit(self, event, *args):
        for handler in self.handlers.get(event, [])[:]:
            handler(*args)


# 1. Таймер
class Timer(Events):
    def __init__(self, seconds):
        super().__init__()
        if seconds < 0:
            raise ValueError("Время должно быть >= 0")
        self.seconds = seconds
        self.paused = False

    def pause(self):
        if not self.paused:
            self.paused = True
            self.emit("pause")

    def resume(self):
        if self.paused:
            self.paused = False
            self.emit("resume")

    async def run(self):
        last, elapsed = monotonic(), 0
        while self.seconds > 0:
            await asyncio.sleep(0.05)
            now = monotonic()
            if not self.paused:
                elapsed += now - last
            last = now

            while elapsed >= 1 and self.seconds > 0:
                elapsed -= 1
                self.seconds -= 1
                self.emit("tick", self.seconds)

        self.emit("finish")


async def timer_demo():
    timer = Timer(3)
    timer.on("tick", lambda n: print("Осталось:", n))
    timer.on("finish", lambda: print("Время вышло!"))
    timer.on("pause", lambda: print("Пауза"))
    timer.on("resume", lambda: print("Продолжение"))

    task = asyncio.create_task(timer.run())
    await asyncio.sleep(1.2)
    timer.pause()
    await asyncio.sleep(2)
    timer.resume()
    await task


# 2. Погодная станция
class WeatherStation(Events):
    def __init__(self):
        super().__init__()
        self.temperature = None

    def subscribe(self, observer):
        self.on("change", observer.update)

    def unsubscribe(self, observer):
        self.off("change", observer.update)

    def set_temperature(self, value):
        if value != self.temperature:
            self.temperature = value
            self.emit("change", value)


class Display:
    def update(self, value):
        print("Температура:", value)


class Logger:
    def __init__(self):
        self.history = []

    def update(self, value):
        self.history.append(value)
        print("Записано:", value)


class Alarm:
    def __init__(self, limit):
        self.limit = limit

    def update(self, value):
        if value > self.limit:
            print("ТРЕВОГА:", value)


def weather_demo():
    station = WeatherStation()
    display, logger, alarm = Display(), Logger(), Alarm(30)

    for observer in (display, logger, alarm):
        station.subscribe(observer)

    # Самоотписка во время уведомления.
    def once(value):
        print("Разовый подписчик:", value)
        station.off("change", once)

    station.on("change", once)
    station.set_temperature(20)
    station.set_temperature(25)
    station.unsubscribe(display)
    station.set_temperature(35)
    station.set_temperature(35)  # Изменения нет — события нет.
    print("История:", logger.history)


# 5. Умный дом
class TemperatureSensor:
    def __init__(self, bus):
        self.bus = bus

    def measure(self, value):
        self.bus.emit("temperature_changed", value)


class Heater:
    def __init__(self, target=22):
        self.target = target
        self.enabled = None

    def update(self, value):
        enabled = value < self.target
        if enabled != self.enabled:
            self.enabled = enabled
            print("Нагреватель:", "ВКЛ" if enabled else "ВЫКЛ")


class RangeAlarm:
    def __init__(self, minimum, maximum):
        self.minimum, self.maximum = minimum, maximum

    def update(self, value):
        if not self.minimum <= value <= self.maximum:
            print("АВАРИЯ: температура вне диапазона:", value)


def home_demo():
    bus = Events()
    sensor = TemperatureSensor(bus)
    heater = Heater()
    logger = Logger()
    alarm = RangeAlarm(5, 30)

    # Все связи задаются снаружи компонентов.
    for component in (heater, logger, alarm):
        bus.on("temperature_changed", component.update)

    for value in (18, 21, 24, 35):
        print("\nИзмерение:", value)
        sensor.measure(value)

    print("История:", logger.history)


if __name__ == "__main__":
    print("1. ТАЙМЕР")
    asyncio.run(timer_demo())

    print("\n2. ПОГОДНАЯ СТАНЦИЯ")
    weather_demo()

    print("\n5. УМНЫЙ ДОМ")
    home_demo()
