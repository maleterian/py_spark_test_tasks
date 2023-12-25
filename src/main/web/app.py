"""
Flask App to execute test tasks
"""

def create_app():
    """ Start app using waitress """
    serve(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    create_app()
    # app.run(host='0.0.0.0', port=8000, debug=True)
