# we will make pydantic schemas so that the data matches our type constraints
# we will be using data types from the library typing to ensure list item types etc.

from pydantic import BaseModel    
from typing import Optional, List

class AnimeResult(BaseModel):
    
    _id: int
    title: str
    synopsis: str
    episodes: int
    score: float
    genres: List[str]
    image_url: str
    similarity: float

class RecommenderRequest(BaseModel):
    
    query: str
    
    # limiting response list to 10 by default
    
    limit: int = 10

    # optional filters the user might choose
    
    min_score: Optional[float] = None # float or None
    genres: Optional[List[str]] = None # list of strings or None

class RecommenderResponse(BaseModel):
    
    query: str
    anime_list: List[AnimeResult]

    # whether this was a response for a vibe query or a similar anime one
    response_type: str 
