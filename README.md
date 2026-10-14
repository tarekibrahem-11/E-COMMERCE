# AI-Powered E-Commerce Platform

An AI-powered e-commerce application that combines product management, semantic search, and generative AI to provide a smarter product discovery and shopping experience.

## Overview

Traditional e-commerce platforms often rely on exact keyword matching, which can make it difficult for users to find products when their search queries do not match product names or descriptions.

This project aims to improve product discovery by integrating AI-powered capabilities into an e-commerce application. It combines a backend API, a product database, semantic search, Retrieval-Augmented Generation (RAG), and an AI assistant to make product exploration more intuitive.

## Key Features

- **Product Management:** Manage and retrieve product information through backend API endpoints.
- **Semantic Product Search:** Search for products based on the meaning and context of a query rather than relying exclusively on exact keyword matches.
- **AI-Powered Search:** Integrate AI capabilities into the product discovery process.
- **AI Shopping Assistant:** Provide an interactive assistant to support users while exploring products.
- **Retrieval-Augmented Generation (RAG):** Supply product-related context to the language model to generate responses grounded in available product information.
- **RESTful API:** Organize backend functionality through API endpoints built with FastAPI.
- **Database Integration:** Store and retrieve product information using SQLAlchemy and SQLite.
- **Web Interface:** Provide a user-facing interface for browsing products and interacting with AI features.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Processing | Pandas |
| Semantic Search | Sentence Transformers, Scikit-learn |
| Generative AI | Google Gemini API |
| AI Architecture | RAG, AI-assisted product discovery |
| Frontend | HTML, CSS, JavaScript |
| Environment Configuration | python-dotenv |

## System Architecture

The application is organized into several components:

### 1. Frontend

The frontend provides the user interface for browsing products, searching the catalog, and interacting with the AI assistant.

### 2. Backend API

FastAPI handles incoming requests, exposes application endpoints, and connects the frontend with the underlying database and AI services.

### 3. Database Layer

SQLite stores product data, while SQLAlchemy provides an ORM layer for interacting with database records through Python.

### 4. Semantic Search Engine

Sentence Transformers are used to generate text embeddings, enabling the application to compare the semantic meaning of search queries with product information. Scikit-learn supports similarity calculations.

### 5. Generative AI and RAG

The AI component uses the Google Gemini API to generate responses. The RAG component prepares relevant product information as context, helping the model produce responses related to the available catalog.

## How It Works

1. Product information is stored in the database.
2. Users browse products or submit search queries through the interface.
3. The backend processes requests and retrieves relevant product information.
4. Semantic search can identify products based on contextual similarity.
5. For AI-assisted interactions, relevant product information can be supplied as context to the language model.
6. The AI assistant generates a response based on the provided context and the user's request.

## Project Goals

- Apply Generative AI to a practical business application.
- Explore semantic search and text embeddings for product discovery.
- Understand how RAG connects external data with large language models.
- Build a structured backend using FastAPI and SQLAlchemy.
- Integrate AI services into a web-based application.
- Develop practical experience in designing AI-powered software systems.

## Skills Demonstrated

- Python application development
- REST API development
- Database integration and ORM usage
- Semantic search and embeddings
- Similarity-based retrieval
- Retrieval-Augmented Generation (RAG)
- Large Language Model API integration
- Frontend and backend integration
- Modular application design

## Future Improvements

- Improve search performance through embedding caching and vector indexing.
- Expand the product catalog and improve data validation.
- Add automated tests for API endpoints and AI components.
- Improve error handling and API reliability.
- Add user authentication and personalized recommendations.
- Introduce evaluation metrics for semantic search and AI-generated responses.
- Improve scalability and deployment readiness.


<img width="1891" height="899" alt="image" src="https://github.com/user-attachments/assets/459533a6-62b7-43d9-b43a-1608c697748c" />
