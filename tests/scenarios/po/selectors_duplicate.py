import robot.utils.asserts as asserts

from robotpageobjects.page import Page as RobotPage, robot_alias

class BaseFoo(object):
    _selectors = {"foo": "foo"}

class BaseBar(object):
    _selectors = {"foo": "bar"}

class Page(RobotPage):
    _selectors = {"foo": "baz"}
