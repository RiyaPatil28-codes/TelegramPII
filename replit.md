# Overview

This is a Flask-based web application called "Telegram PII" that provides secure messaging with advanced Personally Identifiable Information (PII) detection capabilities. The application allows users to register, login, chat with contacts, share stories, and manage their profiles while automatically detecting and protecting sensitive information in messages before they are sent.

# User Preferences

Preferred communication style: Simple, everyday language.
UI Design Preferences: Ultra-minimal single-page authentication interface. Clean design without promotional content, purple styling, or tab buttons. Each authentication form (login/register) shows on separate dedicated pages with simple navigation links. No dual forms on same page - only one form visible at a time.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Authentication Interface**: Modern two-panel layout with clean tabbed forms (auth.html)
- **Design System**: Pure Telegram blue gradient background without purple elements
- **JavaScript Components**: Modular ES6 classes for chat management, PII detection, and stories functionality
- **Real-time Features**: AJAX-based messaging with live PII detection as users type
- **UI Framework**: Bootstrap 5 with Font Awesome icons and custom CSS styling
- **Cache Management**: Cache-busting parameters and no-cache headers for immediate UI updates

## Backend Architecture
- **Web Framework**: Flask with PyMongo for MongoDB integration
- **Application Structure**: Modular design with separate files for routes, models, and core logic
- **Session Management**: Flask sessions with configurable secret keys
- **File Uploads**: Werkzeug-based file handling with size limits (16MB max)
- **Middleware**: ProxyFix for handling reverse proxy headers

## Data Storage
- **Primary Database**: MongoDB for storing users, messages, stories, and chat data
- **Schema Design**: Document-based storage with embedded relationships
- **User Model**: Handles authentication, contacts, and blocked users
- **Message Model**: Stores chat messages with PII detection results
- **Story Model**: Manages ephemeral content with 24-hour expiration

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