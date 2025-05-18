from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, utils, oauth2, database
from .. database import get_db

router = APIRouter(
    prefix="/vote",  # simplify the path operator
    tags=["Vote"]  # groupings are reflected in api docs
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, 
         db: Session = Depends(database.get_db), 
         current_user: int = Depends(oauth2.get_current_user)):
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                     models.Vote.user_id == current_user.id)
    # first check if the post exists
    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {vote.post_id} not found")
    # like and dislike
    found_vote = vote_query.first()
    if (vote.dir == 1):
        if found_vote:  # this user already liked the post
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"already liked post {vote.post_id}")
        # if not liked already:
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": f"You have liked the post {vote.post_id}"}
    else:
        if not found_vote:  # hasn't liked the post yet
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Post not liked yet")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": f"You have unliked the post {vote.post_id}"}