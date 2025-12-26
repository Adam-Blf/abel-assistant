#!/bin/bash
# A.B.E.L - Start Script

echo "🤖 Starting A.B.E.L..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before continuing."
    exit 1
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🔍 Checking API health..."
curl -s http://localhost:8000/health | python -m json.tool

echo ""
echo "✅ A.B.E.L is ONLINE!"
echo ""
echo "📍 Access points:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Adminer: http://localhost:8080"
echo ""
echo "🛑 To stop: docker-compose down"
