# 🎖️ סוכן בדיקת נגישות | Accessibility Audit Agent

סוכן חכם לבדיקת נגישות אתרים המזהה אוטומטית את סוג האתר ודרישות הנגישות שלו.

## ✨ מה הסוכן עושה?

הסוכן מבצע **10+ בדיקות נגישות** אוטומטיות ומציג:
- 🎯 **זיהוי חכם** של סוג האתר (ממשלתי, בנקאות, כללי) והרמה הנדרשת
- 📊 **רמת WCAG שהושגה** - A, AA, AAA או לא עומד בתקן
- ✅ **סטטוס מפורט** - באילו רמות האתר עומד ובאילו לא
- 🔍 **דו"ח מפורט** של כל הבעיות שנמצאו

## 🚀 התקנה והרצה

### דרישות מקדימות
```bash
Python 3.7+
```

### התקנה
```bash
# צור virtual environment
python3 -m venv venv

# הפעל את ה-environment
source venv/bin/activate  # Mac/Linux
# או
venv\Scripts\activate  # Windows

# התקן dependencies
pip install -r requirements.txt
```

### הרצה מהטרמינל
```bash
source venv/bin/activate
python accessibility_agent.py
```

### הרצה עם ממשק Web
```bash
source venv/bin/activate
python app.py
```
אז פתח דפדפן ב: `http://localhost:5000`

## 📋 בדיקות שהסוכן מבצע

### 🔴 קריטי (Level A)
- ✅ שפת הדף (lang attribute)
- ✅ כותרת h1
- ✅ טקסט חלופי לכל התמונות
- ✅ טקסט ברור לכל הקישורים
- ✅ תוויות לכל שדות הטופס
- ✅ טקסט נגיש לכל הכפתורים

### 🟡 חשוב (Level AA)
- ✅ כותרת h1 יחידה
- ✅ היררכיית כותרות תקינה
- ✅ טבלאות עם כותרות
- ✅ אחוז נמוך של בעיות בשדות טופס

### 🟢 מומלץ (Level AAA)
- ✅ ARIA landmarks (main, nav, footer)
- ✅ קישורי דילוג (skip links)
- ✅ מינימום בעיות בינוניות

### 🎨 בדיקות ויזואליות (מוגבל)
- ⚠️ ניגודיות צבעים (בסיסי - דורש כלים מבוססי דפדפן לבדיקה מלאה)

## 🎯 זיהוי אוטומטי של דרישות

הסוכן **מזהה אוטומטית** את סוג האתר ואת רמת הנגישות הנדרשת:

| סוג אתר | רמה נדרשת | דוגמאות |
|---------|-----------|----------|
| **ממשלתי** | AAA | gov.il, משרדי ממשלה |
| **בנקאות ופיננסים** | AA | בנק הפועלים, לאומי, מזרחי |
| **שירותים ציבוריים** | AA | בריאות, חינוך, אוניברסיטאות |
| **מסחר אלקטרוני** | A | חנויות, קניות |
| **כללי** | A (מומלץ) | אתרים אחרים |

## 📊 דוגמה לפלט

```
Accessibility Audit Agent
============================================================

Website: https://example.com

סוג האתר: ממשלתי
רמה נדרשת: Level AAA
רמה שהושגה: Level AA

סטטוס עמידה:
✅ Level A - עומד
✅ Level AA - עומד
❌ Level AAA - לא עומד

Found 3 issues:

MEDIUM PRIORITY ISSUES:
   - Multiple h1
     Found 2 h1 headings. Recommended: 1.

   - Missing ARIA landmarks
     Missing landmarks: main. Landmarks help screen reader users navigate.
```

## 🖥️ ממשק Web

הממשק כולל:
- 🎨 **עיצוב מודרני** עם dark mode
- 📱 **עיצוב רספונסיבי** - עובד מצוין גם במובייל
- 🇮🇱 **תמיכה מלאה בעברית** (RTL)
- ⚡ **אנימציות חלקות**
- 🎯 **תצוגה ויזואלית** של כל הבעיות

### תכונות הממשק
1. **כרטיס מידע על האתר** - סוג האתר והרמה הנדרשת
2. **תג WCAG גדול ובולט** - הרמה שהושגה
3. **גריד סטטוס** - עומד/לא עומד בכל רמה (A, AA, AAA)
4. **כרטיסי סיכום** - מספר בעיות לפי חומרה
5. **רשימת בעיות מפורטת** - עם דוגמאות

## 🔧 טכנולוגיות

- **Backend:** Python, Flask, BeautifulSoup
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **עיצוב:** Custom CSS עם Heebo font
- **Testing:** Requests, lxml

## 📁 מבנה הפרויקט

```
accessibility-agent/
├── accessibility_agent.py   # הסוכן העיקרי
├── app.py                   # Flask server
├── templates/
│   └── index.html          # ממשק משתמש
├── static/
│   ├── style.css           # עיצוב
│   └── script.js           # לוגיקה
├── ACCESSIBILITY_CHECKS.md # תיעוד מפורט של הבדיקות
├── requirements.txt        # תלויות
└── README.md              # המסמך הזה
```

## 🔍 מגבלות ידועות

1. **ניגודיות צבעים** - בדיקה בסיסית בלבד. לבדיקה מלאה יש להשתמש בכלים מבוססי דפדפן
2. **JavaScript динамי** - הסוכן בודק HTML סטטי בלבד
3. **CSS חיצוני** - לא מנתח קבצי CSS חיצוניים
4. **אינטראקציות** - לא בודק keyboard navigation בפועל

## 💡 המלצות לשימוש

1. **הרץ את הבדיקה** לפני כל פרסום של דף חדש
2. **טפל בבעיות קריטיות** תחילה
3. **השתמש בכלים משלימים**:
   - axe DevTools
   - WAVE
   - Lighthouse
   - Color Contrast Analyzer
4. **בדוק עם קוראי מסך** אמיתיים (NVDA, JAWS)
5. **טסט ניווט במקלדת** ידנית

## 📜 רישיון

MIT License - חופשי לשימוש

## 🤝 תרומות

נשמח לתרומות! פתח issue או pull request.

## 📞 יצירת קשר

יש שאלות או הצעות? פתח issue בפרויקט.

---

**נוצר עם ❤️ לשיפור נגישות האינטרנט**
