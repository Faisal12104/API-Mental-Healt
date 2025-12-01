from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime, timedelta
from app.schemas.mood import MoodEntryCreate, MoodEntryResponse, MoodEntryUpdate, MoodStatisticsResponse, MoodAnalysisResponse
from app.utils.database import (
    create_mood_entry, get_mood_entries, get_mood_entry_by_id,
    update_mood_entry, delete_mood_entry, get_mood_statistics, get_mood_distribution
)
from app.utils.mood_analysis import MoodAnalyzer
from app.models.mood import MoodEntry
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mood-entries", tags=["Mood Tracking"])

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
async def create_mood_entry_endpoint(
    mood_data: MoodEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new mood entry
    """
    try:
        logger.info(f"🔍 Creating mood entry for user: {current_user.email}")
        
        # Create mood entry object
        mood_dict = mood_data.dict()
        mood_entry = MoodEntry.from_dict(mood_dict)
        mood_entry.user_id = current_user.id
        
        mood_dict_for_db = mood_entry.to_dict()
        logger.debug(f"🔍 Mood data for DB: {mood_dict_for_db}")
        
        # Save to database
        result = create_mood_entry(mood_dict_for_db)
        if not result:
            logger.error("❌ Failed to create mood entry in database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create mood entry"
            )
        
        logger.info(f"✅ Mood entry created successfully for user: {current_user.email}")
        
        return {
            "success": True,
            "data": {
                "mood_entry": MoodEntryResponse(**mood_dict_for_db)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating mood entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("", response_model=dict)
async def get_mood_entries_endpoint(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    mood: Optional[str] = Query(None, description="Filter by specific mood")
):
    """
    Get mood entries with pagination and filtering
    """
    try:
        logger.info(f"🔍 Getting mood entries for user: {current_user.email}")
        
        # Get entries from database
        entries_data = get_mood_entries(current_user.id, start_date, end_date, page, limit)
        
        # Apply mood filter if provided
        if mood and entries_data:
            entries_data = [entry for entry in entries_data if entry['mood'] == mood]
        
        # Convert to response models
        mood_entries = [MoodEntryResponse(**MoodEntry.from_dict(entry).to_dict()) for entry in entries_data]
        
        # Calculate pagination info
        total_entries = len(entries_data)
        total_pages = (total_entries + limit - 1) // limit
        
        logger.info(f"✅ Retrieved {len(mood_entries)} mood entries for user: {current_user.email}")
        
        return {
            "success": True,
            "data": {
                "mood_entries": mood_entries,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_entries,
                    "total_pages": total_pages
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting mood entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/statistics", response_model=dict)
async def get_mood_statistics_endpoint(
    current_user: User = Depends(get_current_user),
    period: str = Query("week", description="Period: week, month, year")
):
    """
    Get mood statistics for a specific period
    """
    try:
        logger.info(f"🔍 Getting mood statistics for user: {current_user.email}, period: {period}")
        
        # Calculate date range based on period
        end_date = datetime.now().date()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)  # Default to week
        
        # Get statistics from database
        stats = get_mood_statistics(current_user.id, start_date.isoformat(), end_date.isoformat())
        mood_distribution_data = get_mood_distribution(current_user.id, start_date.isoformat(), end_date.isoformat())
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No mood data found for the specified period"
            )
        
        # Process mood distribution
        mood_distribution = {}
        for item in mood_distribution_data:
            mood_distribution[item['mood']] = item['count']
        
        # Get mood entries for trend analysis
        mood_entries = get_mood_entries(current_user.id, start_date.isoformat(), end_date.isoformat(), limit=1000)
        trends = MoodAnalyzer.analyze_trends(mood_entries)
        insights = MoodAnalyzer.generate_insights(stats, trends)
        
        response_data = {
            "period": period,
            "total_entries": stats['total_entries'],
            "average_mood": round(stats['average_mood_score'], 1),
            "average_energy": round(stats['average_energy'], 1) if stats['average_energy'] else 0,
            "average_sleep": round(stats['average_sleep'], 1) if stats['average_sleep'] else 0,
            "mood_distribution": mood_distribution,
            "trends": trends,
            "insights": insights
        }
        
        logger.info(f"✅ Mood statistics generated for user: {current_user.email}")
        
        return {
            "success": True,
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting mood statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/analysis", response_model=dict)
async def get_mood_analysis_endpoint(
    current_user: User = Depends(get_current_user),
    period: str = Query("week", description="Period: week, month, year")
):
    """
    Get detailed mood analysis and recommendations
    """
    try:
        logger.info(f"🔍 Getting mood analysis for user: {current_user.email}, period: {period}")
        
        # Calculate date range
        end_date = datetime.now().date()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get data for analysis
        stats = get_mood_statistics(current_user.id, start_date.isoformat(), end_date.isoformat())
        mood_entries = get_mood_entries(current_user.id, start_date.isoformat(), end_date.isoformat(), limit=1000)
        
        if not stats or not mood_entries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No mood data found for analysis"
            )
        
        # Find dominant mood
        mood_distribution = get_mood_distribution(current_user.id, start_date.isoformat(), end_date.isoformat())
        dominant_mood = max(mood_distribution, key=lambda x: x['count'])['mood'] if mood_distribution else "neutral"
        
        # Calculate consistency score (simplified)
        total_entries = stats['total_entries']
        positive_ratio = stats['positive_days'] / total_entries if total_entries > 0 else 0
        consistency_score = int(positive_ratio * 100)
        
        # Analyze patterns
        patterns = MoodAnalyzer.analyze_patterns(mood_entries)
        
        # Generate recommendations
        recommendations = []
        
        # Sleep recommendations
        avg_sleep = stats.get('average_sleep', 0)
        if avg_sleep < 6:
            recommendations.append({
                "type": "sleep",
                "title": "Tidur Lebih Teratur",
                "description": "Jam tidur Anda di bawah rekomendasi. Coba tidur 7-9 jam per hari.",
                "priority": "high"
            })
        elif avg_sleep > 9:
            recommendations.append({
                "type": "sleep", 
                "title": "Pertahankan Kualitas Tidur",
                "description": "Durasi tidur Anda baik. Pertahankan konsistensi ini.",
                "priority": "low"
            })
        
        # Energy recommendations
        avg_energy = stats.get('average_energy', 0)
        if avg_energy < 5:
            recommendations.append({
                "type": "energy",
                "title": "Tingkatkan Aktivitas Fisik",
                "description": "Olahraga ringan 30 menit sehari bisa meningkatkan energi.",
                "priority": "medium"
            })
        
        # Mood-based recommendations
        if dominant_mood in MoodAnalyzer.NEGATIVE_MOODS:
            recommendations.append({
                "type": "mood",
                "title": "Aktivitas Penambah Mood",
                "description": "Coba aktivitas seperti meditasi, journaling, atau berbicara dengan teman.",
                "priority": "high"
            })
        
        # Add default recommendation if none
        if not recommendations:
            recommendations.append({
                "type": "general",
                "title": "Terus Pantau Mood Anda",
                "description": "Konsistensi dalam melacak mood membantu memahami pola emosional.",
                "priority": "low"
            })
        
        response_data = {
            "dominant_mood": dominant_mood,
            "average_energy": round(avg_energy, 1),
            "average_sleep": round(avg_sleep, 1),
            "consistency_score": consistency_score,
            "positive_days": stats.get('positive_days', 0),
            "correlation": int(patterns.get('energy_correlation', 0) * 100),
            "recommendations": recommendations,
            "patterns": patterns
        }
        
        logger.info(f"✅ Mood analysis completed for user: {current_user.email}")
        
        return {
            "success": True,
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting mood analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{entry_id}", response_model=dict)
async def get_mood_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific mood entry by ID
    """
    try:
        logger.info(f"🔍 Getting mood entry: {entry_id}")
        
        entry_data = get_mood_entry_by_id(entry_id)
        if not entry_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )
        
        # Check if entry belongs to current user
        if entry_data['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        mood_entry = MoodEntryResponse(**MoodEntry.from_dict(entry_data).to_dict())
        
        return {
            "success": True,
            "data": {
                "mood_entry": mood_entry
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting mood entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{entry_id}", response_model=dict)
async def update_mood_entry_endpoint(
    entry_id: str,
    update_data: MoodEntryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a mood entry
    """
    try:
        logger.info(f"🔍 Updating mood entry: {entry_id}")
        
        # Check if entry exists and belongs to user
        existing_entry = get_mood_entry_by_id(entry_id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )
        
        if existing_entry['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update entry
        update_dict = update_data.dict(exclude_unset=True)
        result = update_mood_entry(entry_id, update_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update mood entry"
            )
        
        # Get updated entry
        updated_entry = get_mood_entry_by_id(entry_id)
        mood_entry = MoodEntryResponse(**MoodEntry.from_dict(updated_entry).to_dict())
        
        logger.info(f"✅ Mood entry updated: {entry_id}")
        
        return {
            "success": True,
            "data": {
                "mood_entry": mood_entry
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating mood entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{entry_id}", response_model=dict)
async def delete_mood_entry_endpoint(
    entry_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a mood entry
    """
    try:
        logger.info(f"🔍 Deleting mood entry: {entry_id}")
        
        # Check if entry exists and belongs to user
        existing_entry = get_mood_entry_by_id(entry_id)
        if not existing_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mood entry not found"
            )
        
        if existing_entry['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete entry
        result = delete_mood_entry(entry_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete mood entry"
            )
        
        logger.info(f"✅ Mood entry deleted: {entry_id}")
        
        return {
            "success": True,
            "message": "Mood entry deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting mood entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )