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



class FlaskTest:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.app_context = website.app.app_context()
        self.app_context.push()
        website.db.create_all()
        self.client = website.app.test_client()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        website.db.session.remove()
        website.db.drop_all()

    def get_request(self, endpoint):
        resp = self.client.get(endpoint)
        return resp.get_data(as_text=True)

    def post_request(self, endpoint, payload):
        resp = self.client.post(endpoint, data=payload)
        return resp.get_data(as_text=True)

'''
Test of statically served content: index.html
'''
def test_html():
    with FlaskTest() as ft:
        assert "CS207 Visualizer" in ft.get_request("/")

'''
Test of statically served content: main.js
'''
def test_js():
    with FlaskTest() as ft:
        assert len(ft.get_request("/main.js")) > 0

'''
Test of statically served content: main.css
'''
def test_css():
    with FlaskTest() as ft:
        assert len(ft.get_request("/main.css")) > 0

'''
Test adding a timeseries object via POST
'''
def test_add_ts():
    with FlaskTest() as ft:
        ft.post_request("/timeseries", dict(time_points=[0,1], data_points=[2,3]))