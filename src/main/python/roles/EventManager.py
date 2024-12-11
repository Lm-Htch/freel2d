import time
from multiprocessing.pool import ThreadPool


class EventManager:
    def __init__(self):
        self.events: dict[str, list] = {}

        self.threadPool = ThreadPool(1000)

    def registerEvent(self, eventName: str, eventHandler: callable, args: tuple = (), kwargs=None):
        """
        注册事件
        :param eventName: 事件名
        :param eventHandler: 事件触发方法
        :param args: 方法参数
        :param kwargs: 方法参数
        :return:
        """
        if kwargs is None:
            kwargs = {}
        self.events[eventName] = [eventHandler, args, kwargs]

    def triggerEvent(self, eventName: str):
        """
        触发事件
        :param eventName: 事件名
        :return:
        """
        if eventName in self.events:
            self.events[eventName][0](*self.events[eventName][1], **self.events[eventName][2])
        else:
            print(f"Event {eventName} not found")

    def triggerEventAsync(self, eventName: str):
        """
        异步触发事件
        :param eventName: 事件名
        :return:
        """
        if eventName in self.events:
            self.threadPool.apply_async(self.events[eventName][0], args=self.events[eventName][1], kwds=self.events[eventName][2])
        else:
            print(f"Event {eventName} not found")

    def removeEvent(self, eventName: str):
        """
        移除事件
        :param eventName: 事件名
        :return:
        """
        if eventName in self.events:
            del self.events[eventName]
        else:
            print(f"Event {eventName} not found")

    def clockEvent(self, eventName: str, interval: int, args: tuple = (), kwargs=None):
        """
        注册定时事件
        :param eventName: 事件名
        :param interval: 事件间隔
        :param args: 方法参数
        :param kwargs: 方法参数
        :return:
        """
        if kwargs is None:
            kwargs = {}

        def clock():
            while True:
                self.triggerEvent(eventName)
                time.sleep(interval)

        self.threadPool.apply_async(clock, args=args, kwds=kwargs)


class InformationalNotices:
    def __init__(self, eventManager: EventManager):
        self.eventManager = eventManager
        self.eventManager.registerEvent("informationalNotice", self.informationalNotice)

    def informationalNotice(self, message: str):
        ...
