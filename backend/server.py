from fastapi import FastAPI, Request
from backend.recommender import get_recommendations
from backend.models import RecommenderRequest, RecommenderResponse
from backend.config import lifespan
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import dotenv
import os

dotenv.load_dotenv()

# creating a server
# passing the hook to access variables/data structures

app = FastAPI(lifespan=lifespan)

# adding cross origin request (CORS) middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post("/recommend-anime")

def recommend_anime(req: RecommenderRequest, request : Request):

    print("Recommendation API being called from frontend")
    mode, results = get_recommendations(
        req.query,
        req.limit,
        req.min_score,
        req.genres,
        request.app.state.model,
        request.app.state.titles,
        request.app.state.title_id_pairs
    )

    res = RecommenderResponse(query=req.query,anime_list=results,response_type=mode)
    return res

if __name__ == '__main__':
    port_num = int(os.getenv('PORT_NUM'))
    print("Server running at port: ",port_num)
    uvicorn.run("server:app",host='0.0.0.0',port=port_num,reload=True)