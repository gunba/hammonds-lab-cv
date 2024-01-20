from cv.workflow import azure_wrapper as az

def upload_stored_json(app):
    az.upload_data()
    app.preload()

