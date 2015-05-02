import os



## config for flask

WTF_CSRF_ENABLED = True
SECRET_KEY = 'key'


## config in general
app_path = os.path.dirname(os.path.realpath(__file__)) 
prediction_model_path = app_path + "/../model-serialized/wp-pipeline.pkl"

lib_paths = {
    "lol": app_path + '/../../../lib/',
    "wpmodel": app_path +"/../wpmodel/"
}
