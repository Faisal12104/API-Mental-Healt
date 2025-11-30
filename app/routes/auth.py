from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import RefreshTokenRequest
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.password import hash_password, verify_password
from app.utils.database import (
    create_user, get_user_by_email, get_user_by_id,
    create_refresh_token_db, get_refresh_token, delete_refresh_token,
    delete_user_refresh_tokens
)
from app.models.user import User
from app.models.token import RefreshToken
from app.config import settings
import traceback
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        logger.info(f"🔍 Register attempt for: {user_data.email}")
        
        # Check if user already exists
        logger.info("🔍 Checking if user already exists...")
        existing_user = get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"❌ User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        logger.info("✅ Email is available")

        # Create user dictionary
        logger.info("🔍 Creating user data...")
        user_dict = user_data.dict()
        logger.debug(f"🔍 User data BEFORE processing: {user_dict}")
        
        # Hash password
        logger.info("🔍 Hashing password...")
        hashed_password = hash_password(user_data.password)
        user_dict['password'] = hashed_password
        logger.info("✅ Password hashed successfully")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        user_dict['id'] = user_id
        
        # Create final data for database
        user_data_for_db = {
            'id': user_id,
            'name': user_dict['name'],
            'email': user_dict['email'],
            'password': user_dict['password'],
            'phone': user_dict.get('phone'),
            'date_of_birth': user_dict.get('date_of_birth'),
            'gender': user_dict.get('gender'),
            'avatar': user_dict.get('avatar'),
            'preferences': user_dict.get('preferences', {})
        }
        
        logger.debug(f"🔍 Final user data for DB: {user_data_for_db}")
        
        # Check if password exists
        if 'password' not in user_data_for_db:
            logger.error("❌ Password key missing in user_data_for_db")
            logger.error(f"🔍 Available keys: {list(user_data_for_db.keys())}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing error"
            )

        # Save to database
        logger.info("🔍 Saving user to database...")
        result = create_user(user_data_for_db)
        logger.info(f"🔍 Database create result: {result}")
        
        if not result:
            logger.error("❌ Database create operation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in database"
            )
        logger.info("✅ User saved to database successfully")

        # Create User instance for response (without password)
        user_for_response = User.from_dict(user_data_for_db)

        # Create JWT tokens
        logger.info("🔍 Creating JWT tokens...")
        access_token = create_access_token(data={"sub": user_id, "email": user_data.email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": user_data.email})
        logger.info("✅ Tokens created successfully")

        # Save refresh token to database
        logger.info("🔍 Saving refresh token to database...")
        refresh_token_data = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        refresh_db_result = create_refresh_token_db(refresh_token_data.to_dict())
        
        if not refresh_db_result:
            logger.warning("⚠️  Refresh token might not be saved to database")
        else:
            logger.info("✅ Refresh token saved to database")

        # Prepare response (exclude password from response)
        user_response_data = user_for_response.to_dict()
        user_response_data.pop('password', None)  # Remove password from response
        
        response_data = {
            "success": True,
            "data": {
                "user": UserResponse(**user_response_data),
                "tokens": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "expiresIn": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            }
        }
        
        logger.info(f"🎉 Register successful for: {user_data.email}")
        return response_data
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logger.warning(f"HTTPException in register: {he.detail}")
        raise he
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in register: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """
    Login user and return JWT tokens
    """
    try:
        logger.info(f"🔍 Login attempt for: {login_data.email}")
        
        # Check if user exists
        logger.info("🔍 Checking user existence...")
        user_data = get_user_by_email(login_data.email)
        if not user_data:
            logger.warning(f"❌ User not found: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        logger.info(f"✅ User found: {user_data['email']}")

        # Verify password
        logger.info("🔍 Verifying password...")
        if not verify_password(login_data.password, user_data['password']):
            logger.warning(f"❌ Password verification failed for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        logger.info("✅ Password verified successfully")

        # Create User instance
        user = User.from_dict(user_data)
        logger.info(f"🔍 User object created: {user.email}")

        # Create tokens
        logger.info("🔍 Creating JWT tokens...")
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
        logger.info("✅ Login tokens created")

        # Save refresh token to database
        logger.info("🔍 Saving refresh token to database...")
        refresh_token_data = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        create_refresh_token_db(refresh_token_data.to_dict())
        logger.info("✅ Refresh token saved to database")

        # Prepare response (remove password)
        user_response_data = user.to_dict()
        user_response_data.pop('password', None)
        
        response_data = {
            "success": True,
            "data": {
                "user": UserResponse(**user_response_data),
                "tokens": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "expiresIn": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            }
        }
        
        logger.info(f"🎉 Login successful for: {login_data.email}")
        return response_data
        
    except HTTPException as he:
        logger.warning(f"HTTPException in login: {he.detail}")
        raise he
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in login: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(token_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        logger.info("🔍 Refresh token attempt")
        
        # Verify refresh token from database
        logger.info("🔍 Verifying refresh token in database...")
        db_token = get_refresh_token(token_data.refresh_token)
        if not db_token:
            logger.warning("❌ Refresh token not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        logger.info("✅ Refresh token found in database")

        # Check if token is expired
        logger.info("🔍 Checking token expiration...")
        if datetime.utcnow() > db_token['expires_at']:
            logger.warning("❌ Refresh token expired")
            delete_refresh_token(token_data.refresh_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        logger.info("✅ Refresh token is valid")

        # Verify JWT token and get user data
        logger.info("🔍 Verifying JWT token...")
        token_data_jwt = verify_token(token_data.refresh_token)
        user_data = get_user_by_id(token_data_jwt.user_id)
        
        if not user_data:
            logger.error(f"❌ User not found for ID: {token_data_jwt.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        logger.info(f"✅ User found: {user_data['email']}")

        user = User.from_dict(user_data)

        # Create new access token
        logger.info("🔍 Creating new access token...")
        new_access_token = create_access_token(data={"sub": user.id, "email": user.email})
        logger.info("✅ New access token created")

        response_data = {
            "success": True,
            "data": {
                "accessToken": new_access_token,
                "tokenType": "bearer",
                "expiresIn": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
        logger.info("🎉 Token refresh successful")
        return response_data
    
    except HTTPException as he:
        logger.warning(f"HTTPException in refresh: {he.detail}")
        raise he
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in refresh: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/logout")
async def logout(token_data: RefreshTokenRequest):
    """
    Logout user by deleting refresh token
    """
    try:
        logger.info("🔍 Logout attempt")
        
        # Delete refresh token from database
        logger.info("🔍 Deleting refresh token from database...")
        result = delete_refresh_token(token_data.refresh_token)
        
        if result:
            logger.info("✅ Refresh token deleted successfully")
            response_data = {
                "success": True,
                "message": "Successfully logged out"
            }
        else:
            logger.warning("⚠️  Refresh token might not exist")
            response_data = {
                "success": True,
                "message": "Successfully logged out"
            }
        
        logger.info("🎉 Logout completed")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in logout: {str(e)}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )