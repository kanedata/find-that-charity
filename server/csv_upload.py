import bottle

csv_app = bottle.Bottle()


@csv_app.get('/adddata')
def uploadcsv():
    """
    Form for uploading CSV
    """
    return bottle.template('csv_tool', error=None)
