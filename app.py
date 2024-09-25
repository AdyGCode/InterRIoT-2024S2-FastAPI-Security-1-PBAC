from pathlib import Path

import casbin

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status
from starlette.exceptions import HTTPException

from starlette.middleware.authentication import AuthenticationMiddleware

from fastapi_authz import CasbinMiddleware
from starlette.responses import RedirectResponse, JSONResponse

from basicauth import BasicAuth


# Define a class that holds the details of a person...
class Person(BaseModel):
    name: str


BASE_PATH = Path(__file__).resolve().parent

app = FastAPI(title="FastAPI Templating")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/js", StaticFiles(directory="static/js"), name="js")

TEMPLATES = Jinja2Templates(directory="templates")

enforcer = casbin.Enforcer('./policies/rbac_model.conf', './policies/rbac_policy.csv')

app.add_middleware(CasbinMiddleware, enforcer=enforcer)
app.add_middleware(AuthenticationMiddleware, backend=BasicAuth())


def jsonify(data: dict) -> JSONResponse:
    item_data = jsonable_encoder(data)
    return JSONResponse(content=item_data)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return TEMPLATES.TemplateResponse(
        request=request, name="pages/home.html"
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return TEMPLATES.TemplateResponse(
        request=request, name="pages/about.html"
    )


# API End Points

@app.get('/api/v1')
async def api_v1():
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1 GET by Alice'})
    return JSONResponse(content=item_data, status_code=status.HTTP_200_OK)


# p, alice, /dataset1/resource1, POST
@app.post('/api/v1/dataset1/resource1')
async def dataset1_resource1(data: Person):
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1/Dataset1/Resource1 POST by Alice', 'data': data})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)


# p, alice, /dataset1/*, GET
@app.get('/api/v1/dataset1/*')
async def dataset1():
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1/dataset1/* GET by Alice'})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)


# p, bob, /dataset2/resource1, *
@app.get('/api/v1/dataset2/resource1')
@app.post('/api/v1/dataset2/resource1')
@app.put('/api/v1/dataset2/resource1')
@app.patch('/api/v1/dataset2/resource1')
@app.delete('/api/v1/dataset2/resource1')
async def dataset2_resource1():
    item_data = jsonable_encoder({'success': True, 
                                  'message': 'dataset1/resource1  by BOB'})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)


# p, bob, /dataset2/resource2, GET
@app.get('/api/v1/dataset2/resource2')
async def dataset2_resource1():
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1/dataset2/resource2 GET by Bob'})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)


# p, bob, /dataset2/folder1/*, POST
@app.post('/api/v1/dataset2/folder1')
async def dataset2_resource1():
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1/dataset2/folder1 POST by Bob'})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)


# p, dataset1_admin, /dataset1/*, *
@app.get('/api/v1/dataset1/{rest_of_path}')
@app.post('/api/v1/dataset1/{rest_of_path}')
@app.put('/api/v1/dataset1/{rest_of_path}')
@app.patch('/api/v1/dataset1/{rest_of_path}')
@app.delete('/api/v1/dataset1/{rest_of_path}')
async def dataset1_admin(request: Request, rest_of_path: Path):
    item_data = jsonable_encoder({'success': True, 
                                  'message': '/api/v1/dataset1/... by dataset admin',
                                  'path': rest_of_path})
    return JSONResponse(content=item_data, status_code=status.HTTP_201_CREATED)
