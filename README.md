# Physical AI & Humanoid Robotics Documentation

This is a Docusaurus-based documentation website for the Physical AI & Humanoid Robotics project.

## Installation

```bash
npm install
```

## Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

The `build` directory can be deployed to any web server or hosting service like GitHub Pages, Netlify, or Vercel.

## Project Structure

- `docs/` - Contains all the documentation content in MDX/Markdown format
- `src/css/custom.css` - Custom CSS styles
- `static/` - Static assets like images
- `docusaurus.config.js` - Main Docusaurus configuration
- `sidebars.js` - Navigation sidebar configuration
- `package.json` - Project dependencies and scripts

## Documentation Modules

The documentation is organized into 4 main modules:

1. **Module 1: The Robotic Nervous System (ROS 2)** - Middleware for robot control
2. **Module 2: The Digital Twin (Gazebo & Unity)** - Physics simulation and environment building
3. **Module 3: The AI-Robot Brain (NVIDIA Isaac™)** - Advanced perception and training
4. **Module 4: Vision-Language-Action (VLA)** - Integrating LLMs with robotics for cognitive planning

## Features

- Responsive design for all device sizes
- Dark/light mode support
- Search functionality
- Cross-references between topics
- Code syntax highlighting
- Mathematical notation support
- Interactive elements where needed
- Integrated RAG chatbot for answering questions about the documentation

## Chat Integration

The documentation includes an integrated RAG (Retrieval-Augmented Generation) chatbot that allows users to ask questions about the content directly from the documentation pages.

### Setup

1. Start the backend RAG service:
   ```bash
   cd backend
   poetry install  # or pip install -e .
   poetry run uvicorn rag_agent_service.main:app --reload
   ```

2. Start the Docusaurus documentation site:
   ```bash
   cd docs
   npm start
   ```

### Configuration

The chat interface can be configured using environment variables:

- `REACT_APP_API_BASE_URL` - Backend API URL (default: http://localhost:8000)
- `REACT_APP_API_TIMEOUT` - Request timeout in milliseconds (default: 30000)
- `REACT_APP_API_RETRY_ATTEMPTS` - Number of retry attempts (default: 3)
- `REACT_APP_API_RETRY_DELAY` - Delay between retries in milliseconds (default: 1000)

### Usage

The chat interface is available on pages where the ChatInterface component is included. Users can type questions about the documentation content and receive AI-generated answers with source citations.