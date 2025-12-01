from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
from app.schemas.consultation import ConsultationCreate, ConsultationResponse, ConsultationUpdate, ConsultationStatusUpdate
from app.utils.database import (
    create_consultation, get_consultations, get_consultation_by_id, 
    update_consultation, get_consultation_statistics, get_psychologist_by_id
)
from app.models.consultation import Consultation
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultations", tags=["Consultations"])

# Dependency untuk mendapatkan current user
async def get_current_user(token: str = Depends(verify_token)):
    from app.utils.database import get_user_by_id
    user_data = get_user_by_id(token.user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return User.from_dict(user_data)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_consultation_endpoint(
    consultation_data: ConsultationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new consultation request
    """
    try:
        logger.info(f"🔍 Creating consultation for user: {current_user.email}")
        
        # Check if psychologist exists and is available
        psychologist = get_psychologist_by_id(consultation_data.psychologist_id)
        if not psychologist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Psychologist not found"
            )
        
        if not psychologist.get('is_available', True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Psychologist is not available for new consultations"
            )
        
        # Create consultation object
        consultation_dict = consultation_data.dict()
        consultation = Consultation.from_dict(consultation_dict)
        consultation.user_id = current_user.id
        consultation.price = psychologist.get('price_per_hour', 0) * (consultation.duration / 60)
        
        consultation_dict_for_db = consultation.to_dict()
        logger.debug(f"🔍 Consultation data: {consultation_dict_for_db}")
        
        # Save to database
        result = create_consultation(consultation_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create consultation"
            )
        
        logger.info(f"✅ Consultation created for user: {current_user.email}")
        
        return {
            "success": True,
            "data": {
                "consultation": ConsultationResponse(**consultation_dict_for_db)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating consultation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("", response_model=dict)
async def get_user_consultations(
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get user's consultations with filtering
    """
    try:
        logger.info(f"🔍 Getting consultations for user: {current_user.email}")
        
        consultations_data = get_consultations(user_id=current_user.id, status=status, page=page, limit=limit)
        consultations = [ConsultationResponse(**Consultation.from_dict(consult).to_dict()) for consult in consultations_data]
        
        # Get psychologist details for each consultation
        for consultation in consultations:
            psychologist = get_psychologist_by_id(consultation.psychologist_id)
            if psychologist:
                consultation.psychologist_name = psychologist['name']
        
        logger.info(f"✅ Retrieved {len(consultations)} consultations for user: {current_user.email}")
        
        return {
            "success": True,
            "data": consultations
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting consultations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{consultation_id}", response_model=dict)
async def get_consultation_detail(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get consultation details by ID
    """
    try:
        logger.info(f"🔍 Getting consultation: {consultation_id}")
        
        consultation_data = get_consultation_by_id(consultation_id)
        if not consultation_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        # Check if consultation belongs to user
        if consultation_data['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        consultation = ConsultationResponse(**Consultation.from_dict(consultation_data).to_dict())
        
        # Add psychologist details
        psychologist = get_psychologist_by_id(consultation.psychologist_id)
        if psychologist:
            consultation.psychologist_name = psychologist['name']
            consultation.psychologist_avatar = psychologist.get('avatar')
        
        return {
            "success": True,
            "data": {
                "consultation": consultation
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting consultation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{consultation_id}/status", response_model=dict)
async def update_consultation_status(
    consultation_id: str,
    status_data: ConsultationStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update consultation status
    """
    try:
        logger.info(f"🔍 Updating consultation status: {consultation_id}")
        
        consultation_data = get_consultation_by_id(consultation_id)
        if not consultation_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        # Check if consultation belongs to user
        if consultation_data['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        update_dict = status_data.dict(exclude_unset=True)
        
        # Handle status-specific logic
        if status_data.status == 'cancelled':
            update_dict['cancelled_at'] = datetime.now()
        elif status_data.status == 'completed':
            update_dict['completed_at'] = datetime.now()
        
        result = update_consultation(consultation_id, update_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update consultation status"
            )
        
        updated_consultation = get_consultation_by_id(consultation_id)
        consultation = ConsultationResponse(**Consultation.from_dict(updated_consultation).to_dict())
        
        logger.info(f"✅ Consultation status updated: {consultation_id} -> {status_data.status}")
        
        return {
            "success": True,
            "data": {
                "consultation": consultation
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating consultation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{consultation_id}/start", response_model=dict)
async def start_consultation_session(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Start a consultation session
    """
    try:
        logger.info(f"🔍 Starting consultation session: {consultation_id}")
        
        consultation_data = get_consultation_by_id(consultation_id)
        if not consultation_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        # Check if consultation belongs to user and is confirmed
        if consultation_data['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if consultation_data['status'] != 'confirmed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consultation must be confirmed before starting"
            )
        
        update_dict = {
            'status': 'completed',  # Auto-complete when started (for demo)
            'started_at': datetime.now(),
            'completed_at': datetime.now()
        }
        
        result = update_consultation(consultation_id, update_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start consultation session"
            )
        
        logger.info(f"✅ Consultation session started: {consultation_id}")
        
        return {
            "success": True,
            "message": "Consultation session started successfully",
            "data": {
                "session_started_at": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error starting consultation session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/statistics/overview", response_model=dict)
async def get_consultation_statistics_overview(
    current_user: User = Depends(get_current_user)
):
    """
    Get consultation statistics for user
    """
    try:
        logger.info(f"🔍 Getting consultation statistics for user: {current_user.email}")
        
        stats = get_consultation_statistics(current_user.id)
        
        response_data = {
            "total_sessions": stats.get('total_sessions', 0),
            "completed_sessions": stats.get('completed_sessions', 0),
            "pending_sessions": stats.get('pending_sessions', 0),
            "upcoming_sessions": stats.get('upcoming_sessions', 0),
            "total_hours": round(stats.get('total_minutes', 0) / 60, 1),
            "total_spent": stats.get('total_spent', 0)
        }
        
        logger.info(f"✅ Consultation statistics retrieved for user: {current_user.email}")
        
        return {
            "success": True,
            "data": response_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting consultation statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )