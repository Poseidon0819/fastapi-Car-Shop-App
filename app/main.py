from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .src.dependencies import get_query_token, get_token_header
from .src.internal import admin
from .src.routers import items, users, cars, stocks, sellers, buyers, sales

from .src.database import engine, SessionLocal, Base

# Database Auto Generation
Base.metadata.create_all(bind=engine)

# Add validation on all routes
# app = FastAPI(dependencies=[Depends(get_query_token)])

app = FastAPI()

route_prefix_v1 = "/api/v1"

# Request Mapping
app.include_router(users.router, prefix=route_prefix_v1)
app.include_router(items.router, prefix=route_prefix_v1)
app.include_router(cars.router, prefix=route_prefix_v1)
app.include_router(stocks.router, prefix=route_prefix_v1)
app.include_router(sellers.router, prefix=route_prefix_v1)
app.include_router(buyers.router, prefix=route_prefix_v1)
app.include_router(sales.router, prefix=route_prefix_v1)

# Example of Admin creation
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

# Allow CORS from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session per request
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    '''
    The middleware we'll add (just a function) will create
    a new SQLAlchemy SessionLocal for each request, add it to
    the request and then close it once the request is finished.
    '''
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response
