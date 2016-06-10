import robot.utils.asserts as asserts

from robotpageobjects.page import Page as RobotPage, robot_alias

class BaseFoo(object):
    selectors = {"foo": "foo"}

class BaseBar(object):
    selectors = {"foo": "bar"}

class Page(RobotPage):
    selectors = {"foo": "baz"}
