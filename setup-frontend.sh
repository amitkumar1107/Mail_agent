#!/bin/bash
# Quick setup script for AI Mail Assistant Frontend

echo "🚀 AI Mail Assistant Frontend Setup"
echo "===================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Change to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created. Update it with your configuration:"
    echo "   - VITE_API_URL=http://localhost:8000/api"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Start the backend: cd backend && python manage.py runserver"
echo "   2. Start the frontend: cd frontend && npm run dev"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "🎉 Happy coding!"
