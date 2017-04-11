from bottle import request, response
from bottle import post, get, put, delete

@post('/names')
def screen_stock():
    '''Handles name creation'''
    data = request.json()
    screen_type = data["__type__"]
