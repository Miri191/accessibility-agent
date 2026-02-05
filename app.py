from flask import Flask, render_template, request, jsonify, make_response
from accessibility_agent import AccessibilityAgent
import traceback
import json
from datetime import datetime

app = Flask(__name__)

# Store last audit result for download
last_audit_result = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def audit():
    global last_audit_result
    
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please provide a URL'}), 400
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Run the audit
        agent = AccessibilityAgent(url)
        
        if not agent.fetch_page():
            return jsonify({'error': 'Failed to fetch the page. Please check the URL.'}), 400
        
        # Run all checks
        agent.check_lang_attribute()
        agent.check_headings_hierarchy()
        agent.check_images_alt_text()
        agent.check_links_text()
        agent.check_form_labels()
        agent.check_buttons()
        agent.check_tables()
        agent.check_aria_landmarks()
        agent.check_skip_links()
        agent.check_color_contrast()
        
        # Calculate summary
        total_issues = sum(len(issues) for issues in agent.issues.values())
        
        # Calculate WCAG conformance level
        wcag_level = agent.calculate_wcag_level()
        
        result = {
            'success': True,
            'url': url,
            'issues': agent.issues,
            'total_issues': total_issues,
            'wcag_level': wcag_level,
            'stats': agent.stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store for download
        last_audit_result = result
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download-report')
def download_report():
    """Download detailed accessibility report"""
    global last_audit_result
    
    if not last_audit_result:
        return jsonify({'error': 'No audit data available. Please run an audit first.'}), 400
    
    # Create detailed report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("דוח נגישות מפורט | Detailed Accessibility Report")
    report_lines.append("=" * 80)
    report_lines.append(f"\nאתר נבדק: {last_audit_result['url']}")
    report_lines.append(f"תאריך: {last_audit_result['timestamp']}")
    report_lines.append(f"\nסוג האתר: {last_audit_result['wcag_level']['site_type']}")
    report_lines.append(f"רמה נדרשת: {last_audit_result['wcag_level']['required_level']}")
    report_lines.append(f"רמה שהושגה: {last_audit_result['wcag_level']['achieved_label']}")
    report_lines.append(f"\n{last_audit_result['wcag_level']['achieved_description']}")
    
    report_lines.append("\n" + "=" * 80)
    report_lines.append("סטטוס עמידה ברמות WCAG")
    report_lines.append("=" * 80)
    for level, info in last_audit_result['wcag_level']['all_levels'].items():
        status = "✅ עומד" if info['passes'] else "❌ לא עומד"
        report_lines.append(f"\n{info['label']}: {status}")
        report_lines.append(f"   {info['description']}")
    
    report_lines.append("\n" + "=" * 80)
    report_lines.append("סיכום בעיות")
    report_lines.append("=" * 80)
    report_lines.append(f"\nסה\"כ בעיות: {last_audit_result['total_issues']}")
    report_lines.append(f"קריטיות: {len(last_audit_result['issues']['critical'])}")
    report_lines.append(f"גבוהות: {len(last_audit_result['issues']['high'])}")
    report_lines.append(f"בינוניות: {len(last_audit_result['issues']['medium'])}")
    report_lines.append(f"נמוכות: {len(last_audit_result['issues']['low'])}")
    
    # Priority order and Hebrew names
    priorities = [
        ('critical', 'קריטיות'),
        ('high', 'גבוהות'),
        ('medium', 'בינוניות'),
        ('low', 'נמוכות')
    ]
    
    for priority_key, priority_name in priorities:
        issues = last_audit_result['issues'][priority_key]
        if issues:
            report_lines.append(f"\n{'=' * 80}")
            report_lines.append(f"בעיות {priority_name} ({len(issues)})")
            report_lines.append("=" * 80)
            
            for i, issue in enumerate(issues, 1):
                report_lines.append(f"\n{i}. {issue['type']}")
                report_lines.append(f"   {issue['details']}")
                
                if 'count' in issue:
                    report_lines.append(f"   מספר מופעים: {issue['count']}")
                
                if 'examples' in issue and issue['examples']:
                    report_lines.append(f"   דוגמאות:")
                    for example in issue['examples'][:5]:
                        report_lines.append(f"      - {example}")
    
    report_lines.append("\n" + "=" * 80)
    report_lines.append("סטטיסטיקות מפורטות")
    report_lines.append("=" * 80)
    report_lines.append(f"\nתמונות: {last_audit_result['stats']['total_images']} סה\"כ, {last_audit_result['stats']['images_without_alt']} ללא alt")
    report_lines.append(f"קישורים: {last_audit_result['stats']['total_links']} סה\"כ, {last_audit_result['stats']['unclear_links']} לא ברורים")
    report_lines.append(f"שדות טופס: {last_audit_result['stats']['total_forms']} סה\"כ, {last_audit_result['stats']['forms_without_labels']} ללא labels")
    report_lines.append(f"כפתורים: {last_audit_result['stats']['total_buttons']} סה\"כ, {last_audit_result['stats']['buttons_without_text']} ללא טקסט")
    report_lines.append(f"טבלאות: {last_audit_result['stats']['total_tables']} סה\"כ, {last_audit_result['stats']['tables_without_headers']} ללא headers")
    report_lines.append(f"כותרות H1: {last_audit_result['stats']['h1_count']}")
    report_lines.append(f"שפת הדף: {'כן' if last_audit_result['stats']['has_lang'] else 'לא'}")
    
    report_lines.append("\n" + "=" * 80)
    report_lines.append("סוף הדוח")
    report_lines.append("=" * 80)
    
    report_text = "\n".join(report_lines)
    
    # Create response with UTF-8 encoding
    response = make_response(report_text)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=accessibility-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    
    return response

@app.route('/download-json')
def download_json():
    """Download audit data as JSON"""
    global last_audit_result
    
    if not last_audit_result:
        return jsonify({'error': 'No audit data available'}), 400
    
    response = make_response(json.dumps(last_audit_result, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=accessibility-data-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
