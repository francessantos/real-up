import json
import requests
from requests_toolbelt import MultipartEncoder

base_url = "http://localhost:81/"

########################
# Homepage Test
########################
def test_homepage():
    response = requests.get(
            base_url
        )
    assert 200 == response.status_code


########################
# Create REAL-UP's map test
########################
def test_create_map():
    mp_encoder = MultipartEncoder(
        fields={
            'scenario-group':'chicago',
            'period-group': '3'
        }
    )

    headers = {'Content-Type': mp_encoder.content_type}

    response = requests.post(
            base_url+'realup-map',
            data=mp_encoder,
            headers=headers
        )
    assert 200 == response.status_code