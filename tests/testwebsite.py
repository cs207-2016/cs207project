''''

Authors:
Sophie Hilgard
Ryan Lapcevic
Anthony Soroka
Ariel Herbert-Voss
Yamini Bansal

Date: 14 Dec 2016
Course: Project CS 207
Document: test_website.py
Summary: Testing Flask Webserver

Example:
    Example how to run this test
        $ source activate py35
        $ py.test testwebsite.py

'''


from context import *


'''
Functions Being Tested: Len
Summary: Basic Len Test
'''
def test_len():
    website.db.create_all()
    with website.app.test_request_context("/") as context:
        website.app.preprocess_request()
        resp = website.app.process_response(website.root())
        resp.direct_passthrough = False
        assert "CS207 Visualizer" in str(resp.data)