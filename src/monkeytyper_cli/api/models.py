from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class BaseTestStats(BaseModel):
    wpm: Optional[float] = None
    acc: Optional[float] = None
    raw: Optional[float] = None
    consistency: Optional[float] = None
    difficulty: Optional[str] = None # e.g., "normal", "expert"
    testType: Optional[str] = Field(None, alias="testType") # e.g., "words_10"

class UserStatsData(BaseModel):
    testsStarted: Optional[int] = Field(None, alias="testsStarted")
    testsCompleted: Optional[int] = Field(None, alias="testsCompleted")
    timeTyping: Optional[float] = Field(None, alias="timeTyping") # In seconds?

class UserStatsResponse(BaseModel):
    message: Optional[str] = None
    data: Optional[UserStatsData] = None

class PersonalBestEntry(BaseTestStats):
    timestamp: Optional[int] = None

class PersonalBestsData(BaseModel):
    bests: Optional[Dict[str, PersonalBestEntry]] = None

class PersonalBestsResponse(BaseModel):
    message: Optional[str] = None
    data: Optional[PersonalBestsData] = None

class LeaderboardEntry(BaseModel):
    rank: Optional[int] = None
    uid: Optional[str] = None # User ID
    name: Optional[str] = None
    wpm: Optional[float] = None
    acc: Optional[float] = None
    raw: Optional[float] = None
    timestamp: Optional[int] = None

class LeaderboardResponse(BaseModel):
    message: Optional[str] = None
    data: List[LeaderboardEntry] = []
