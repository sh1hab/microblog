import json
import requests
from flask_babel import _
# from myapp import application
from flask import current_app


def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' in current_app.config or current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not required')
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'westus2'}
    r = requests.post(
        'https://api.cognitive.microsofttranslator.com'
        '/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}])
    if r.status_code != 200:
        return _('Error: the translation service failed')
    return r.json()[0]['translation']['0']['text']