from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.user import UserResponse, UserUpdate
from app.utils.database import get_user_by_id, update_user, delete_user_refresh_tokens
from app.auth.jwt_handler import verify_token
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

async def get_current_user(token: str = Depends(verify_token)):
    user_data = get_user_by_id(token.user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return User.from_dict(user_data)

@router.get("/profile", response_model=dict)
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "user": UserResponse(**current_user.to_dict())
        }
    }

@router.put("/profile", response_model=dict)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    update_dict = update_data.dict(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    result = update_user(current_user.id, update_dict)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Get updated user data
    updated_user_data = get_user_by_id(current_user.id)
    updated_user = User.from_dict(updated_user_data)
    
    return {
        "success": True,
        "data": {
            "user": UserResponse(**updated_user.to_dict())
        }
    }

@router.get("/data-export")
async def export_data(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "user": UserResponse(**current_user.to_dict()),
            "exported_at": datetime.now().isoformat(),
            "format": "json"
        }
    }

@router.delete("/data")
async def delete_data(current_user: User = Depends(get_current_user)):
    delete_user_refresh_tokens(current_user.id)
    
    return {
        "success": True,
        "message": "User data deletion scheduled"
    }