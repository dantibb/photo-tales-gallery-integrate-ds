#!/bin/bash

# Clear Down with Backup Script
# This script creates a backup of the current database and then clears everything down

set -e  # Exit on any error

echo "=== Photo Tales Clear Down with Backup Script ==="
echo ""

# Create backup directory with timestamp
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup directory: $BACKUP_DIR"
echo ""

# Check if PostgreSQL is running
if docker-compose ps | grep -q "photo_tales_postgres.*Up"; then
    echo "🐘 PostgreSQL is running, attempting database backup..."
    
    # Check if the photo_tales database exists
    DB_EXISTS=$(docker-compose exec -T postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='photo_tales'")
    
    if [ "$DB_EXISTS" = "1" ]; then
        echo "📊 Database 'photo_tales' exists, creating backup..."
        
        # Create database backup
        BACKUP_FILE="$BACKUP_DIR/database_backup.sql"
        docker-compose exec -T postgres pg_dump -U postgres -d photo_tales > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            echo "✅ Database backup created: $BACKUP_FILE"
            echo "   Size: $(du -h "$BACKUP_FILE" | cut -f1)"
        else
            echo "❌ Database backup failed!"
            exit 1
        fi
    else
        echo "📊 Database 'photo_tales' does not exist yet, skipping backup"
    fi
    
    # Backup local files
    echo ""
    echo "📄 Backing up local files..."
    
    if [ -f "photo_tales.db" ]; then
        cp "photo_tales.db" "$BACKUP_DIR/"
        echo "✅ SQLite database backed up"
    fi
    
    if [ -f "local_contexts.json" ]; then
        cp "local_contexts.json" "$BACKUP_DIR/"
        echo "✅ Local contexts backed up"
    fi
    
    if [ -d "interviews" ]; then
        cp -r "interviews" "$BACKUP_DIR/"
        echo "✅ Interviews directory backed up"
    fi
    
    if [ -d "chroma_db" ]; then
        cp -r "chroma_db" "$BACKUP_DIR/"
        echo "✅ ChromaDB directory backed up"
    fi
    
    echo ""
    echo "🔄 Stopping and removing containers..."
    docker-compose down -v
    
    echo "🗑️  Removing volumes..."
    docker volume rm backend_postgres_data backend_pgadmin_data 2>/dev/null || true
    
    echo "🧹 Cleaning up local files..."
    rm -f photo_tales.db local_contexts.json
    rm -rf interviews chroma_db flask_session
    
    echo ""
    echo "🚀 Starting fresh database..."
    docker-compose up -d
    
    echo ""
    echo "⏳ Waiting for database to initialize..."
    sleep 10
    
    echo ""
    echo "✅ Clear down completed successfully!"
    echo "📦 Backup saved in: $BACKUP_DIR"
    echo ""
    if [ "$DB_EXISTS" = "1" ]; then
        echo "To restore from backup:"
        echo "  docker-compose exec -T postgres psql -U postgres -d photo_tales < $BACKUP_FILE"
    fi
    
else
    echo "🐘 PostgreSQL is not running, skipping backup..."
    echo ""
    echo "🔄 Stopping any existing containers..."
    docker-compose down -v 2>/dev/null || true
    
    echo "🗑️  Removing volumes..."
    docker volume rm backend_postgres_data backend_pgadmin_data 2>/dev/null || true
    
    echo "🧹 Cleaning up local files..."
    rm -f photo_tales.db local_contexts.json
    rm -rf interviews chroma_db flask_session
    
    echo ""
    echo "🚀 Starting fresh database..."
    docker-compose up -d
    
    echo ""
    echo "⏳ Waiting for database to initialize..."
    sleep 10
    
    echo ""
    echo "✅ Clear down completed successfully!"
    echo "📦 Backup saved in: $BACKUP_DIR"
fi

echo ""
echo "🎯 Next steps:"
echo "  1. Start the Flask backend: python3 main.py"
echo "  2. Test the endpoints: curl http://localhost:8080/health"
echo "  3. Add some test data through the API"
echo ""
echo "=== Script completed ==="
