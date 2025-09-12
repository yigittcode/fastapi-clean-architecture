# FastAPI Learning Project

A modern REST API built with FastAPI, demonstrating best practices for web development, authentication, and database operations.

## 🚀 Features

- **Modern Architecture**: Clean separation of concerns with controllers, routers, models, and schemas
- **Repository Pattern**: Data access layer with generic CRUD operations
- **Full Async Support**: True asynchronous database operations with AsyncSession
- **JWT Authentication**: Secure token-based authentication system
- **PostgreSQL Database**: Production-ready database with SQLAlchemy ORM and async driver (asyncpg)
- **Input Validation**: Robust data validation using Pydantic
- **Structured Logging**: Request tracking and performance monitoring
- **Global Exception Handling**: Consistent error responses
- **Dependency Injection**: Clean and testable code structure
- **Security Features**: Rate limiting, CORS, security headers
- **Frontend UI**: Simple HTML/CSS/JS interface for testing
- **API Documentation**: Auto-generated Swagger/ReDoc documentation
- **Performance Optimized**: Connection pooling, eager loading, efficient queries

## 📁 Project Structure

```
fastapi_learning/
├── app/
│   ├── controllers/          # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── items.py
│   │   └── users.py
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py         # Application settings
│   │   ├── database.py       # Async database configuration
│   │   ├── deps.py           # Async dependency injection
│   │   ├── exceptions.py     # Exception handlers
│   │   ├── logging.py        # Structured logging
│   │   ├── middleware.py     # Custom middleware
│   │   └── security.py       # Authentication utilities
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── user.py
│   ├── repositories/         # Data access layer (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── base.py           # Generic CRUD operations
│   │   ├── item.py           # Item-specific queries
│   │   └── user.py           # User-specific queries
│   ├── routers/              # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   ├── items.py          # Items CRUD
│   │   └── users.py          # User management
│   └── schemas/              # Pydantic models (DTOs)
│       ├── __init__.py
│       ├── auth.py
│       ├── item.py
│       └── user.py
├── frontend/                 # Simple web interface
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies (including asyncpg)
├── .env                      # Environment variables
├── .env.example              # Environment template
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd fastapi_learning
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE fastapi_learning;
```

### 5. Environment Variables

Create a `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fastapi_learning

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=FastAPI Learning API
VERSION=1.0.0
DEBUG=true
```

### 6. Run Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 7. Open Frontend

Open `frontend/index.html` in your browser to test the API with a simple UI.

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - User login (JSON)
- `POST /auth/login/form` - User login (Form data, OAuth2 compatible)
- `POST /auth/register` - User registration

### Users
- `GET /users/me/` - Get current user profile
- `GET /users/` - List all users (Admin only)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user (Admin only)

### Items
- `GET /items/` - List all items (with pagination)
- `GET /items/my/` - Get current user's items
- `GET /items/{item_id}` - Get item by ID
- `POST /items/` - Create new item
- `PUT /items/{item_id}` - Update item (Owner only)
- `DELETE /items/{item_id}` - Delete item (Owner only)

### System
- `GET /` - API information
- `GET /health` - Health check

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register** a new user or use the default admin account
2. **Login** to receive an access token
3. **Include token** in requests: `Authorization: Bearer <token>`

### Default Admin User
- **Username**: `admin`
- **Password**: `Admin123!`

## 🧪 Testing with Frontend

1. Open `frontend/index.html` in your browser
2. Register a new user or login with existing credentials
3. Add, edit, and delete items
4. View your profile and items

## 🧪 Testing with curl

### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Create Item
```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "My First Item",
    "description": "This is a test item"
  }'
```

## 🏗️ Architecture Patterns

### Controller Pattern
Business logic is separated from route handlers:
- **Controllers**: Handle business logic
- **Routers**: Handle HTTP requests/responses
- **Models**: Database entities
- **Schemas**: Data validation and serialization

### Dependency Injection
Clean dependency management with FastAPI's DI system:
```python
DatabaseDep = Annotated[AsyncSession, Depends(get_async_db)]  # Always async - modern approach
ActiveUserDep = Annotated[User, Depends(get_current_active_user)]
```

### Exception Handling
Centralized error handling with custom exceptions:
- HTTP exceptions
- Business logic errors
- Validation errors
- Database errors

## 🔧 Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (keep secret!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DEBUG`: Enable/disable debug mode

## 📊 Logging

Structured logging with request tracking:
- Request/response logging
- Performance monitoring
- Error tracking
- User activity logs

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for password security
- **Input Validation**: Pydantic model validation
- **Rate Limiting**: API request throttling
- **CORS**: Cross-origin request handling
- **Security Headers**: XSS protection, content type sniffing prevention

## 🚀 Deployment

For production deployment:

1. Set `DEBUG=false` in environment
2. Use a strong `SECRET_KEY`
3. Configure production database
4. Use a reverse proxy (nginx)
5. Enable HTTPS
6. Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is for learning purposes. Feel free to use and modify as needed.

## 🏗️ Architecture Patterns

### Repository Pattern
The application uses the Repository pattern for data access:

```python
# Generic base repository with common CRUD operations
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType
    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType
    async def delete(self, db: AsyncSession, id: Any) -> ModelType

# Specialized repositories inherit from base
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]
```

### Async Database Operations
Full async support with SQLAlchemy 2.0+ and asyncpg:

```python
# Async engine and session
async_engine = create_async_engine("postgresql+asyncpg://...")
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession)

# Async dependency injection
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Clean Architecture Layers
1. **Routers**: HTTP request/response handling
2. **Controllers**: Business logic and validation
3. **Repositories**: Data access and persistence
4. **Models**: Database entities
5. **Schemas**: Data transfer objects (DTOs)

## 🔧 Technology Stack

### Backend
- **FastAPI 0.104+**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.0+**: Async ORM with modern Python support
- **asyncpg 0.29+**: Fast PostgreSQL async driver
- **Pydantic 2.5+**: Data validation using Python type annotations
- **Python-JOSE**: JWT token handling
- **Passlib**: Password hashing
- **Structlog**: Structured logging

### Database
- **PostgreSQL**: Production-ready relational database
- **Async Connection Pool**: High-performance database connections
- **Migration Support**: Database schema versioning with Alembic

### Development
- **Uvicorn**: ASGI server with auto-reload
- **Rich**: Beautiful terminal output
- **Type Hints**: Full typing support for better IDE experience

## 🎯 Learning Objectives

This project demonstrates:

- ✅ Modern FastAPI application structure
- ✅ Repository Pattern implementation
- ✅ Full async/await database operations
- ✅ RESTful API design principles
- ✅ Authentication and authorization
- ✅ Database operations with async ORM
- ✅ Input validation and error handling
- ✅ Structured logging and monitoring
- ✅ Security best practices
- ✅ Frontend integration
- ✅ API documentation
- ✅ Performance optimization techniques
- ✅ Clean architecture principles

Perfect for learning FastAPI and modern web development practices!