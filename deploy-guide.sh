#!/bin/bash

echo "🚀 מדריך העלאה מהירה ל-GitHub + Render"
echo "=========================================="
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI מותקן"
    echo ""
    echo "האם תרצה ליצור repository אוטומטית? (y/n)"
    read -r response
    
    if [ "$response" = "y" ]; then
        echo "🔄 יוצר repository חדש ב-GitHub..."
        gh repo create accessibility-agent --public --source=. --remote=origin --push
        echo ""
        echo "✅ הפרויקט הועלה ל-GitHub!"
        echo ""
        echo "🌐 עכשיו:"
        echo "1. היכנס ל-https://render.com"
        echo "2. לחץ 'New +' → 'Web Service'"
        echo "3. חבר את הרפוזיטורי שיצרת"
echo "4. הגדרות:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
        echo "5. לחץ 'Create Web Service'"
        echo ""
        echo "זהו! תקבל URL חי תוך דקות! 🎉"
    fi
else
    echo "ℹ️  GitHub CLI לא מותקן"
    echo ""
    echo "📝 הוראות ידניות:"
    echo "1. היכנס ל-https://github.com/new"
    echo "2. צור repository חדש בשם 'accessibility-agent'"
    echo "3. הרץ את הפקודות הבאות:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR-USERNAME/accessibility-agent.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "4. אחרי זה:"
    echo "   - היכנס ל-https://render.com"
    echo "   - לחץ 'New +' → 'Web Service'"
    echo "   - חבר את הרפוזיטורי"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
    echo ""
    echo "✅ הפרויקט מוכן ל-deployment!"
fi
