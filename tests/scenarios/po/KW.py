from robot.api import logger

class KW(object):

    def say_hi_to(self, to, frm=" Joe"):
        out = "Hi, %s from %s" %(to, frm)
        logger.console(out)

    def say_hi_to2(self, frm=" Joe"):
        out = "Hi, Mary from %s" % frm
        logger.console(out)

    def say_hi_to3(self, to=None, frm=None):
        out = "Hi, %s from %s" % (to, frm)
        logger.console(out)

    def say_hi_to4(self, to=None, **kwargs):
        out = "Hi, %s from %s" % (to, kwargs["frm"])
        logger.console(out)

    def say_hi_to5(self, to=None, foo="bar", **kwargs):
        out = "Hi, %s from %s" % (to, kwargs["frm"])
        logger.console(out)

    def say_hi_to6(self, a=None, foo="bar", **kwargs):
        out = "Hi, %s from %s" % (kwargs["to"], kwargs["frm"])
        logger.console(out)

if __name__ == "__main__":
    o = KW()
    o.say_hi_to("Mary", frm=" Daniel")
    o.say_hi_to2(frm="Daniel")
    o.say_hi_to3(to="Mary", frm="Daniel")
    o.say_hi_to4(to="Mary", frm="Daniel")
    o.say_hi_to5(to="Mary", frm="Daniel")
    o.say_hi_to6(to="Mary", frm="Daniel")