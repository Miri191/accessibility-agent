const form = document.getElementById('auditForm');
const urlInput = document.getElementById('urlInput');
const auditBtn = document.getElementById('auditBtn');
const btnText = document.querySelector('.btn-text');
const spinner = document.querySelector('.spinner');
const results = document.getElementById('results');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const successMessage = document.getElementById('successMessage');
const issuesList = document.getElementById('issuesList');

const priorityNames = {
    'critical': 'קריטי',
    'high': 'גבוה',
    'medium': 'בינוני',
    'low': 'נמוך'
};

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = urlInput.value.trim();
    if (!url) return;

    // Reset UI
    hideError();
    hideResults();
    setLoading(true);

    try {
        const response = await fetch('/audit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'שגיאה בביצוע הבדיקה');
        }

        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    auditBtn.disabled = loading;
    if (loading) {
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function displayResults(data) {
    const { url, issues, total_issues, wcag_level } = data;

    // Update tested URL
    const testedUrlElement = document.getElementById('testedUrl');
    testedUrlElement.textContent = url;
    testedUrlElement.href = url;

    // Update WCAG Level Badge
    displayWCAGLevel(wcag_level);

    // Update summary cards
    document.getElementById('totalIssues').textContent = total_issues;
    document.getElementById('criticalCount').textContent = issues.critical.length;
    document.getElementById('highCount').textContent = issues.high.length;
    document.getElementById('mediumCount').textContent = issues.medium.length;

    // Clear previous issues
    issuesList.innerHTML = '';

    if (total_issues === 0) {
        successMessage.classList.remove('hidden');
        issuesList.classList.add('hidden');
    } else {
        successMessage.classList.add('hidden');
        issuesList.classList.remove('hidden');

        // Display issues by priority
        ['critical', 'high', 'medium', 'low'].forEach(priority => {
            if (issues[priority] && issues[priority].length > 0) {
                issues[priority].forEach(issue => {
                    const issueCard = createIssueCard(issue, priority);
                    issuesList.appendChild(issueCard);
                });
            }
        });
    }

    results.classList.remove('hidden');

    // Smooth scroll to results
    setTimeout(() => {
        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function displayWCAGLevel(wcagLevel) {
    // Update compact header
    document.getElementById('siteTypeCompact').textContent = wcagLevel.site_type;

    // Map required level to Hebrew label
    const levelLabels = {
        'level_a': 'Level A',
        'level_aa': 'Level AA',
        'level_aaa': 'Level AAA'
    };
    document.getElementById('requiredLevelCompact').textContent = levelLabels[wcagLevel.required_level] || wcagLevel.required_level;

    // Update achieved level indicator
    const achievedIndicator = document.getElementById('achievedLevelCompact');
    achievedIndicator.textContent = wcagLevel.achieved_label;
    achievedIndicator.classList.remove('level_aaa', 'level_aa', 'level_a', 'non_compliant');
    achievedIndicator.classList.add(wcagLevel.achieved_level);

    // Update quick status grid
    updateQuickStatus('quickStatusA', wcagLevel.all_levels.level_a.passes);
    updateQuickStatus('quickStatusAA', wcagLevel.all_levels.level_aa.passes);
    updateQuickStatus('quickStatusAAA', wcagLevel.all_levels.level_aaa.passes);
}

function updateQuickStatus(elementId, passes) {
    const element = document.getElementById(elementId);
    element.classList.remove('passed', 'failed');
    element.classList.add(passes ? 'passed' : 'failed');
}

// Download function
function downloadPDF() {
    window.location.href = '/download-report';
}



function createIssueCard(issue, priority) {
    const card = document.createElement('div');
    card.className = `issue-card ${priority}`;

    const header = document.createElement('div');
    header.className = 'issue-header';

    const badge = document.createElement('span');
    badge.className = `issue-badge ${priority}`;
    badge.textContent = priorityNames[priority];

    const title = document.createElement('div');
    title.className = 'issue-title';
    title.textContent = issue.type;

    header.appendChild(badge);
    header.appendChild(title);

    const details = document.createElement('div');
    details.className = 'issue-details';
    details.textContent = issue.details;

    card.appendChild(header);
    card.appendChild(details);

    // Add count if available
    if (issue.count) {
        const countBadge = document.createElement('div');
        countBadge.className = 'issue-count';
        countBadge.textContent = `נמצאו: ${issue.count} מקרים`;
        card.appendChild(countBadge);
    }

    // Add fix recommendation
    const recommendation = getFixRecommendation(issue.type);
    if (recommendation) {
        const fixDiv = document.createElement('div');
        fixDiv.className = 'issue-fix';
        fixDiv.innerHTML = `
            <div class="fix-title">💡 איך לתקן:</div>
            <div class="fix-content">${recommendation}</div>
        `;
        card.appendChild(fixDiv);
    }

    // Add examples if available
    if (issue.examples && issue.examples.length > 0) {
        const examplesDiv = document.createElement('div');
        examplesDiv.className = 'issue-examples';

        const examplesTitle = document.createElement('h4');
        examplesTitle.textContent = 'דוגמאות:';

        const examplesList = document.createElement('ul');
        issue.examples.forEach(example => {
            const li = document.createElement('li');
            li.textContent = example;
            examplesList.appendChild(li);
        });

        examplesDiv.appendChild(examplesTitle);
        examplesDiv.appendChild(examplesList);
        card.appendChild(examplesDiv);
    }

    return card;
}

function getFixRecommendation(issueType) {
    const recommendations = {
        'Missing h1': 'הוסף כותרת &lt;h1&gt; לדף. כותרת H1 חייבת להיות הראשונה והיחידה בדף ולתאר את התוכן העיקרי.',
        'Multiple h1': 'השאר רק &lt;h1&gt; אחת בדף. שנה כותרות נוספות ל-&lt;h2&gt; או &lt;h3&gt; לפי ההיררכיה.',
        'Skipped heading level': 'תקן את סדר הכותרות: H1 → H2 → H3. אל תדלג רמות (למשל מ-H1 ישר ל-H3).',
        'Missing alt text': 'הוסף תכונת alt לכל התמונות: &lt;img src="..." alt="תיאור התמונה"&gt;. תמונות דקורטיביות צריכות alt="".',
        'Missing lang attribute': 'הוסף lang לתג HTML: &lt;html lang="he"&gt; (עברית) או &lt;html lang="en"&gt; (אנגלית).',
        'Unclear links': 'החלף טקסטים כמו "לחץ כאן" בתיאור ברור: "להורדת הטופס" או הוסף aria-label="תיאור ברור".',
        'Form inputs without labels': 'קשר label לכל שדה: &lt;label for="name"&gt;שם:&lt;/label&gt;&lt;input id="name"&gt; או השתמש ב-aria-label.',
        'Buttons without accessible text': 'הוסף טקסט לכפתורים: &lt;button&gt;שלח&lt;/button&gt; או aria-label="שלח טופס".',
        'Tables without headers': 'הוסף &lt;th&gt; לכותרות הטבלה או השתמש ב-scope="col" / scope="row".',
        'Missing ARIA landmarks': 'הוסף &lt;main&gt;, &lt;nav&gt;, &lt;footer&gt; או role="main", role="navigation".',
        'Missing skip link': 'הוסף קישור "דלג לתוכן" בראש הדף: &lt;a href="#main"&gt;דלג לתוכן&lt;/a&gt;.',
        'Color contrast check limited': 'השתמש בכלי בדיקת ניגודיות (Contrast Checker) לבדוק שיחס הניגודיות לפחות 4.5:1 לטקסט רגיל.'
    };

    return recommendations[issueType] || null;
}


// Add some sample URLs for quick testing
const sampleUrls = [
    'google.com',
    'example.com',
    'github.com'
];

// Optional: Add autocomplete suggestions
urlInput.addEventListener('focus', function () {
    if (!this.value) {
        this.placeholder = 'לדוגמה: ' + sampleUrls[Math.floor(Math.random() * sampleUrls.length)];
    }
});
