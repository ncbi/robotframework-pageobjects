from robot.libraries.BuiltIn import BuiltIn


ROBOT_LISTENER_API_VERSION = 2
session_id = None

def end_keyword(name, attrs):
    if "Open" in name:
        se2 =  BuiltIn().get_library_instance('Selenium2Library')
        global session_id
        session_id = se2._current_browser().session_id
        print "Tag running Sauce job, with session_id: %s" % session_id

def end_test(name, attrs):
    global session_id
    print "report %s status for session ID: %s" % (name, session_id)
