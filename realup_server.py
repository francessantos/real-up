"""Main module for API route definitions"""

import uvicorn

from datetime import datetime

from fastapi import FastAPI, Body, HTTPException, Depends, Request
from fastapi.security.api_key import APIKey
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from requests_toolbelt.multipart import decoder
from starlette.status import HTTP_403_FORBIDDEN

from src.config import log

import src.routes.map_plot


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def handle(response: (dict, int)):
    """Checks if the response of a route contains an error.
    If it does, raises an HTTPException.
    """
    result, status = response
    if status >= 400:
        # Error happened
        raise HTTPException(status, detail=result)

    return result

### App ###
@app.get('/',summary="",description="",response_class=HTMLResponse)
async def index(request: Request):
    log('real-up.homepage',{'event':'start'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return templates.TemplateResponse("index.html",{"request": request})


@app.post('/realup-map', response_class=HTMLResponse)
async def create_realup_map(request: Request):
    body = await request.body()
    sbody = body.decode()
    header = dict(request.headers)
    data = {}
    for part in decoder.MultipartDecoder(body, header["content-type"]).parts:
        name = part.headers[b'Content-Disposition'].decode().split(';')[1][7:-1]
        if name != "action":
            data[name] = part.text
        else:
            pass    
    city = data.get("scenario-group",None)
    period = data.get("period-group",None)

    log('real-up.map_plot',{'event':'start', 'city':city, 'period':period}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    result, status = await src.routes.map_plot.handler(city, period)
    log('real-up.map_plot',{'event':'end', 'status':status, 'city':city, 'period':period}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if status != 200:
        return templates.TemplateResponse("error.html",{"request": request, "data": result})

    return templates.TemplateResponse("layout.html",{"request": request, "data": result})


### Main ###
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)