# Overview

This is a Flask-based web application called "Telegram PII" that provides secure messaging with advanced Personally Identifiable Information (PII) detection capabilities. The application features a modern blue-themed authentication interface followed by a dark-themed chat dashboard with pre-added chatbots. Users can register, login, and interact with various specialized bots including AI Assistant, PII Detector, News Bot, Weather Bot, Translator Bot, and Code Helper.

# User Preferences

Preferred communication style: Simple, everyday language.
UI Design Preferences: Ultra-minimal single-page authentication interface with modern premium styling. Clean design without promotional content or tab buttons. Each authentication form (login/register) shows on separate dedicated pages with simple navigation links. Features animated gradient backgrounds, glassmorphism effects, enhanced button animations, and modern rounded corners. No dual forms on same page - only one form visible at a time. Full-screen Telegram-style chat interface with seamless light theme, no white borders, and professional messaging aesthetics.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Authentication Interface**: Ultra-minimal single-page forms with separate login/register routes
- **Design System**: Full-screen Telegram-style interface with light theme, seamless white backgrounds, and professional messaging aesthetics
- **Chat Interface**: Modern light-themed dashboard with light gray sidebar (#f7f7f7) containing pre-added bots, full-screen design without borders
- **JavaScript Components**: Interactive ChatManager class for real-time bot conversations
- **Bot System**: 6 personalized friends with natural personalities, personal interests, and genuine conversational responses that focus on building friendships rather than providing services
- **UI Framework**: Bootstrap 5 with Font Awesome icons and custom CSS styling
- **Cache Management**: Cache-busting parameters and no-cache headers for immediate UI updates

## Backend Architecture
- **Web Framework**: Flask with PyMongo for MongoDB integration
- **Application Structure**: Modular design with separate files for routes, models, and core logic
- **Session Management**: Flask sessions with configurable secret keys
- **File Uploads**: Werkzeug-based file handling with size limits (16MB max)
- **Middleware**: ProxyFix for handling reverse proxy headers

## Data Storage
- **Current Implementation**: MongoDB Atlas cloud database with Flask-PyMongo integration
- **User Storage**: MongoStorage class handling user authentication, profile data, and chat messages
- **Message Persistence**: All chat conversations stored in MongoDB with PII detection results
- **Bot Personalities**: 6 friends with natural personalities - Sarah Chen (movie lover who enjoys deep conversations), Alex Rodriguez (outdoor adventurer into hiking and photography), Maya Patel (curious person who loves hearing people's stories), David Kim (astronomy enthusiast who prefers real conversations), Elena Kowalski (multicultural foodie who traveled the world), and Ryan O'Connor (gamer and music lover who values human connections)
- **Session Management**: Flask sessions for user state and authentication with MongoDB ObjectId user tracking
- **Database Collections**: users (authentication & profiles), messages (chat history with PII analysis)

## Authentication & Authorization
- **Password Security**: Werkzeug password hashing with salt
- **Session-based Auth**: Flask sessions for user state management
- **User Registration**: Email-based account creation with duplicate prevention
- **Profile Management**: User profile updates including avatar uploads

## PII Detection System
- **NLP Processing**: spaCy English model for named entity recognition
- **Pattern Matching**: Regex patterns for detecting emails, phone numbers, Aadhar cards, PAN cards, credit cards, and passport numbers
- **Machine Learning**: TF-IDF vectorization with DBSCAN and KMeans clustering for advanced PII detection
- **Real-time Analysis**: Client-side and server-side PII detection with caching
- **Confidence Scoring**: Configurable confidence thresholds for PII detection accuracy

## Configuration Management
- **Environment Variables**: Centralized config with development defaults
- **Security Settings**: Configurable session secrets and debug modes
- **PII Settings**: Adjustable confidence thresholds and logging preferences
- **Upload Configuration**: Configurable file size limits and storage paths

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **PyMongo**: MongoDB driver for Python
- **Werkzeug**: WSGI utilities and security helpers

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **JavaScript**: Native ES6 for client-side functionality

## NLP and Machine Learning
- **spaCy**: Natural language processing library with English model
- **scikit-learn**: Machine learning library for TF-IDF and clustering algorithms
- **NumPy**: Numerical computing for ML operations

## Database
- **MongoDB**: NoSQL document database for data persistence
- **Local Development**: Default connection to localhost:27017
- **Production**: Configurable via MONGO_URI environment variable

## Development Tools
- **Logging**: Python's built-in logging module for debugging
- **Environment Configuration**: OS environment variables for deployment flexibility