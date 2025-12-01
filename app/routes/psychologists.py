from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.psychologist import PsychologistResponse, PsychologistCreate, PsychologistUpdate
from app.utils.database import create_psychologist, get_psychologists, get_psychologist_by_id, update_psychologist
from app.models.psychologist import Psychologist
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/psychologists", tags=["Psychologists"])

@router.get("", response_model=dict)
async def get_psychologists_list(
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get list of psychologists with filtering
    """
    try:
        logger.info(f"🔍 Getting psychologists list - specialization: {specialization}, available: {available}")
        
        psychologists_data = get_psychologists(specialization, available, page, limit)
        psychologists = [PsychologistResponse(**Psychologist.from_dict(psych).to_dict()) for psych in psychologists_data]
        
        logger.info(f"✅ Retrieved {len(psychologists)} psychologists")
        
        return {
            "success": True,
            "data": psychologists
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting psychologists: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{psychologist_id}", response_model=dict)
async def get_psychologist_detail(psychologist_id: str):
    """
    Get psychologist details by ID
    """
    try:
        logger.info(f"🔍 Getting psychologist details: {psychologist_id}")
        
        psychologist_data = get_psychologist_by_id(psychologist_id)
        if not psychologist_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Psychologist not found"
            )
        
        psychologist = PsychologistResponse(**Psychologist.from_dict(psychologist_data).to_dict())
        
        return {
            "success": True,
            "data": psychologist
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting psychologist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Admin routes (protected)
@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_psychologist_endpoint(
    psychologist_data: PsychologistCreate,
    token: str = Depends(verify_token)
):
    """
    Create a new psychologist (Admin only)
    """
    try:
        logger.info(f"🔍 Creating psychologist: {psychologist_data.name}")
        
        psychologist_dict = psychologist_data.dict()
        psychologist = Psychologist.from_dict(psychologist_dict)
        psychologist_dict_for_db = psychologist.to_dict()
        
        result = create_psychologist(psychologist_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create psychologist"
            )
        
        logger.info(f"✅ Psychologist created: {psychologist_data.name}")
        
        return {
            "success": True,
            "data": {
                "psychologist": PsychologistResponse(**psychologist_dict_for_db)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating psychologist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{psychologist_id}", response_model=dict)
async def update_psychologist_endpoint(
    psychologist_id: str,
    update_data: PsychologistUpdate,
    token: str = Depends(verify_token)
):
    """
    Update psychologist details (Admin only)
    """
    try:
        logger.info(f"🔍 Updating psychologist: {psychologist_id}")
        
        existing_psychologist = get_psychologist_by_id(psychologist_id)
        if not existing_psychologist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Psychologist not found"
            )
        
        update_dict = update_data.dict(exclude_unset=True)
        result = update_psychologist(psychologist_id, update_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update psychologist"
            )
        
        updated_psychologist = get_psychologist_by_id(psychologist_id)
        psychologist = PsychologistResponse(**Psychologist.from_dict(updated_psychologist).to_dict())
        
        logger.info(f"✅ Psychologist updated: {psychologist_id}")
        
        return {
            "success": True,
            "data": {
                "psychologist": psychologist
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating psychologist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )