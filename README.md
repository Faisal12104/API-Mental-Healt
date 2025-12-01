# 🧠 Mental Health App - API Specification

## 📋 Overview
API untuk aplikasi kesehatan mental yang mencakup konsultasi psikolog, mood tracking, forum curhat, dan analisis data kesehatan mental.

## 🔗 Base URL
```
Production: https://api.mentalhealth.app/v1
Development: https://dev-api.mentalhealth.app/v1
```

## 🔐 Authentication
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **Refresh Token**: 30 days
- **Access Token**: 24 hours

---

## 👤 User Management

### 1. User Registration
```http
POST /auth/register
```

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "phone": "string",
  "dateOfBirth": "YYYY-MM-DD",
  "gender": "male|female|other",
  "preferences": {
    "notifications": true,
    "anonymousMode": false,
    "themes": ["anxiety", "depression", "relationships"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "string",
      "email": "string",
      "phone": "string",
      "dateOfBirth": "YYYY-MM-DD",
      "gender": "string",
      "avatar": "string",
      "createdAt": "ISO 8601",
      "updatedAt": "ISO 8601"
    },
    "tokens": {
      "accessToken": "jwt_token",
      "refreshToken": "jwt_token",
      "expiresIn": 86400
    }
  }
}
```

### 2. User Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

### 3. Get User Profile
```http
GET /users/profile
```

### 4. Update User Profile
```http
PUT /users/profile
```

### 5. Refresh Token
```http
POST /auth/refresh
```

---

## 🧠 Mood Tracking

### 1. Create Mood Entry
```http
POST /mood-entries
```

**Request Body:**
```json
{
  "mood": "veryHappy|happy|neutral|sad|verySad|anxious|stressed|calm|excited|angry",
  "energyLevel": 1-10,
  "sleepHours": 3-12,
  "activities": ["exercise", "reading", "socializing", "work", "hobby"],
  "tags": ["productive", "tired", "motivated", "stressed"],
  "note": "string",
  "timestamp": "ISO 8601"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "userId": "uuid",
    "mood": "string",
    "energyLevel": 8,
    "sleepHours": 7,
    "activities": ["exercise", "reading"],
    "tags": ["productive", "motivated"],
    "note": "Had a great day!",
    "timestamp": "2024-01-15T10:30:00Z",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Get Mood Entries
```http
GET /mood-entries?page=1&limit=20&startDate=2024-01-01&endDate=2024-01-31
```

**Query Parameters:**
- `page`: int (default: 1)
- `limit`: int (default: 20, max: 100)
- `startDate`: YYYY-MM-DD
- `endDate`: YYYY-MM-DD
- `mood`: filter by specific mood

### 3. Get Mood Statistics
```http
GET /mood-entries/statistics?period=week|month|year
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "week",
    "totalEntries": 7,
    "averageMood": 6.5,
    "averageEnergy": 7.2,
    "averageSleep": 7.8,
    "moodDistribution": {
      "happy": 3,
      "neutral": 2,
      "sad": 1,
      "anxious": 1
    },
    "trends": {
      "moodTrend": "improving",
      "energyTrend": "stable",
      "sleepTrend": "declining"
    },
    "insights": [
      "Your mood has improved 15% this week",
      "Sleep quality affects your energy levels"
    ]
  }
}
```

### 4. Get Mood Analysis
```http
GET /mood-entries/analysis?period=week|month|year
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dominantMood": "happy",
    "averageEnergy": 6.3,
    "averageSleep": 7.1,
    "consistencyScore": 75,
    "positiveDays": 4,
    "correlation": 85,
    "recommendations": [
      {
        "type": "sleep",
        "title": "Tidur Lebih Teratur",
        "description": "Jam tidur Anda bervariasi. Coba tidur pada jam yang sama setiap hari.",
        "priority": "high"
      },
      {
        "type": "exercise",
        "title": "Tingkatkan Aktivitas Fisik",
        "description": "Olahraga ringan 30 menit sehari bisa membantu meningkatkan mood.",
        "priority": "medium"
      }
    ],
    "patterns": {
      "weeklyPattern": "mood_improves_weekend",
      "energyCorrelation": 0.85,
      "sleepImpact": "high"
    }
  }
}
```

---

## 👨‍⚕️ Consultation Management

### 1. Get Psychologists List
```http
GET /psychologists?specialization=anxiety|depression|relationships&available=true
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Dr. Sarah Johnson",
      "specialization": ["anxiety", "depression"],
      "experience": 8,
      "rating": 4.8,
      "pricePerHour": 150000,
      "languages": ["Indonesian", "English"],
      "availability": {
        "monday": ["09:00-17:00"],
        "tuesday": ["09:00-17:00"],
        "wednesday": ["09:00-17:00"]
      },
      "avatar": "string",
      "bio": "string"
    }
  ]
}
```

### 2. Create Consultation Request
```http
POST /consultations
```

**Request Body:**
```json
{
  "psychologistId": "uuid",
  "type": "chat|video|phone",
  "preferredDate": "YYYY-MM-DD",
  "preferredTime": "HH:MM",
  "duration": 60,
  "reason": "string",
  "urgency": "low|medium|high"
}
```

### 3. Get User Consultations
```http
GET /consultations?status=pending|confirmed|completed|cancelled
```

### 4. Update Consultation Status
```http
PUT /consultations/{consultationId}/status
```

**Request Body:**
```json
{
  "status": "confirmed|completed|cancelled",
  "notes": "string"
}
```

### 5. Start Consultation Session
```http
POST /consultations/{consultationId}/start
```

---

## 💬 Chat & Messaging

### 1. Send Message
```http
POST /consultations/{consultationId}/messages
```

**Request Body:**
```json
{
  "content": "string",
  "type": "text|image|file",
  "attachments": ["url1", "url2"]
}
```

### 2. Get Messages
```http
GET /consultations/{consultationId}/messages?page=1&limit=50
```

### 3. Mark Messages as Read
```http
PUT /consultations/{consultationId}/messages/read
```

---

## 🏘️ Forum Management

### 1. Get Forum Rooms
```http
GET /forum/rooms?category=cinta|pekerjaan|keluarga&page=1&limit=20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rooms": [
      {
        "id": "uuid",
        "name": "Curhat Cinta",
        "description": "Ruang untuk berbagi cerita tentang hubungan dan cinta",
        "category": "cinta",
        "icon": "💕",
        "memberCount": 1250,
        "postCount": 89,
        "lastActivity": "2024-01-15T14:30:00Z",
        "isJoined": false,
        "rules": ["Be respectful", "No spam", "Keep it anonymous if needed"]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "totalPages": 3
    }
  }
}
```

### 2. Join/Leave Room
```http
POST /forum/rooms/{roomId}/join
DELETE /forum/rooms/{roomId}/leave
```

### 3. Create Room
```http
POST /forum/rooms
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "category": "cinta|pekerjaan|keluarga|kesehatan|pendidikan|hobi",
  "icon": "string",
  "isPrivate": false,
  "rules": ["string"]
}
```

### 4. Get Room Details
```http
GET /forum/rooms/{roomId}
```

---

## 📝 Forum Posts

### 1. Create Post
```http
POST /forum/rooms/{roomId}/posts
```

**Request Body:**
```json
{
  "content": "string",
  "isAnonymous": true,
  "mood": "😊|😢|😰|😠|😌|🤩",
  "tags": ["string"],
  "attachments": ["url1", "url2"]
}
```

### 2. Get Posts
```http
GET /forum/rooms/{roomId}/posts?page=1&limit=20&sort=newest|popular
```

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "uuid",
        "roomId": "uuid",
        "authorId": "uuid",
        "authorName": "Anonymous User",
        "authorAvatar": "string",
        "content": "Halo semua! Saya sedang merasa cemas...",
        "isAnonymous": true,
        "mood": "😰",
        "tags": ["anxiety", "work"],
        "likeCount": 15,
        "commentCount": 8,
        "shareCount": 2,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z",
        "isLiked": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "totalPages": 8
    }
  }
}
```

### 3. Like/Unlike Post
```http
POST /forum/posts/{postId}/like
DELETE /forum/posts/{postId}/like
```

### 4. Share Post
```http
POST /forum/posts/{postId}/share
```

### 5. Report Post
```http
POST /forum/posts/{postId}/report
```

**Request Body:**
```json
{
  "reason": "spam|inappropriate|harassment|other",
  "description": "string"
}
```

---

## 💬 Comments

### 1. Create Comment
```http
POST /forum/posts/{postId}/comments
```

**Request Body:**
```json
{
  "content": "string",
  "isAnonymous": false
}
```

### 2. Get Comments
```http
GET /forum/posts/{postId}/comments?page=1&limit=20
```

### 3. Like Comment
```http
POST /forum/comments/{commentId}/like
```

---

## 📊 Analytics & Insights

### 1. Get User Dashboard
```http
GET /dashboard
```

**Response:**
```json
{
  "success": true,
  "data": {
    "moodStats": {
      "totalEntries": 45,
      "currentStreak": 7,
      "averageMood": 6.8,
      "moodTrend": "improving"
    },
    "consultationStats": {
      "totalSessions": 3,
      "upcomingSessions": 1,
      "totalHours": 4.5
    },
    "forumStats": {
      "postsCount": 12,
      "commentsCount": 45,
      "roomsJoined": 3
    },
    "achievements": [
      {
        "id": "uuid",
        "name": "Mood Tracker",
        "description": "Tracked mood for 7 consecutive days",
        "icon": "🏆",
        "unlockedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "recommendations": [
      {
        "type": "mood",
        "title": "Great job tracking your mood!",
        "description": "You've been consistent for 7 days. Keep it up!",
        "action": "continue_tracking"
      }
    ]
  }
}
```

### 2. Get Trending Topics
```http
GET /forum/trending?period=day|week|month
```

### 3. Get User Insights
```http
GET /insights?type=mood|sleep|energy|social
```

---

## 🔔 Notifications

### 1. Get Notifications
```http
GET /notifications?page=1&limit=20&unreadOnly=true
```

### 2. Mark as Read
```http
PUT /notifications/{notificationId}/read
```

### 3. Mark All as Read
```http
PUT /notifications/read-all
```

---

## 📱 App Configuration

### 1. Get App Settings
```http
GET /settings
```

### 2. Update Settings
```http
PUT /settings
```

**Request Body:**
```json
{
  "notifications": {
    "moodReminder": true,
    "consultationReminder": true,
    "forumUpdates": false
  },
  "privacy": {
    "anonymousMode": false,
    "dataSharing": false
  },
  "themes": ["anxiety", "depression", "relationships"]
}
```

---

## 🚨 Emergency & Crisis Support

### 1. Get Crisis Resources
```http
GET /crisis/resources
```

### 2. Report Crisis
```http
POST /crisis/report
```

**Request Body:**
```json
{
  "type": "self_harm|suicidal_thoughts|severe_depression",
  "severity": "low|medium|high|critical",
  "description": "string",
  "location": "string"
}
```

---

## 📊 Admin & Moderation

### 1. Get Reported Content
```http
GET /admin/reports?status=pending|reviewed|resolved
```

### 2. Moderate Content
```http
PUT /admin/reports/{reportId}
```

**Request Body:**
```json
{
  "action": "approve|reject|warn|ban",
  "reason": "string",
  "moderatorNotes": "string"
}
```

### 3. Get User Analytics
```http
GET /admin/analytics/users?period=week|month|year
```

---

## 🔒 Security & Privacy

### 1. Data Export (GDPR)
```http
GET /users/data-export
```

### 2. Data Deletion
```http
DELETE /users/data
```

### 3. Privacy Settings
```http
GET /users/privacy
PUT /users/privacy
```

---

## 📈 Health & Monitoring

### 1. Health Check
```http
GET /health
```

### 2. API Status
```http
GET /status
```

---

## 🎯 Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Codes
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

---

## 📝 Rate Limiting

- **General API**: 1000 requests/hour per user
- **Mood Entries**: 10 requests/hour per user
- **Forum Posts**: 50 requests/hour per user
- **Messages**: 200 requests/hour per user

---

## 🔄 Webhooks

### 1. Consultation Events
- `consultation.created`
- `consultation.confirmed`
- `consultation.completed`
- `consultation.cancelled`

### 2. Forum Events
- `post.created`
- `post.liked`
- `post.reported`
- `comment.created`

### 3. User Events
- `user.registered`
- `mood.entry.created`
- `crisis.reported`

---

## 📱 Mobile App Specific

### 1. Push Notifications
```http
POST /notifications/push/register
```

**Request Body:**
```json
{
  "deviceToken": "string",
  "platform": "ios|android",
  "appVersion": "1.0.0"
}
```

### 2. Offline Sync
```http
POST /sync/upload
GET /sync/download
```

---

## 🧪 Testing Endpoints

### 1. Test Data Generation
```http
POST /test/generate-data
```

### 2. Reset User Data
```http
POST /test/reset-user/{userId}
```

---

## 📊 API Metrics

- **Response Time**: < 200ms (95th percentile)
- **Uptime**: 99.9%
- **Error Rate**: < 0.1%
- **Throughput**: 10,000 requests/minute

---

## 🔧 Development Tools

### 1. API Documentation
- **Swagger UI**: `/docs`
- **OpenAPI Spec**: `/openapi.json`

### 2. Testing
- **Postman Collection**: Available in repository
- **Test Environment**: `https://test-api.mentalhealth.app`

### 3. Monitoring
- **Health Check**: `/health`
- **Metrics**: `/metrics`
- **Logs**: Available via logging service

---

## 📋 Implementation Priority

### Phase 1 (MVP)
1. User Authentication
2. Mood Tracking
3. Basic Forum
4. Simple Analytics

### Phase 2 (Enhanced)
1. Consultation System
2. Advanced Analytics
3. Notifications
4. Crisis Support

### Phase 3 (Advanced)
1. AI Insights
2. Advanced Moderation
3. Integration APIs
4. Admin Dashboard

---

## 🚀 Deployment

### Environments
- **Development**: `dev-api.mentalhealth.app`
- **Staging**: `staging-api.mentalhealth.app`
- **Production**: `api.mentalhealth.app`

### Database
- **Primary**: PostgreSQL
- **Cache**: Redis
- **Search**: Elasticsearch
- **Files**: AWS S3

### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CDN**: CloudFlare
- **Monitoring**: Prometheus + Grafana

---

*This API specification covers all features implemented in the Mental Health App and provides a comprehensive foundation for backend development.*
