from flask import Flask, render_template, request, jsonify, make_response
from accessibility_agent import AccessibilityAgent
import traceback
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

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
    """Download detailed accessibility report as PDF"""
    global last_audit_result
    
    if not last_audit_result:
        return jsonify({'error': 'No audit data available. Please run an audit first.'}), 400
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Create custom styles for Hebrew text (right-to-left)
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'HebrewTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2563eb')
    )
    
    # Heading style (RTL)
    heading_style = ParagraphStyle(
        'HebrewHeading',
        parent=styles['Heading2'],
        alignment=TA_RIGHT,
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#1e40af')
    )
    
    # Normal text style (RTL)
    normal_style = ParagraphStyle(
        'HebrewNormal',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=11,
        spaceAfter=8
    )
    
    # Build PDF content
    # Title
    elements.append(Paragraph('Detailed Accessibility Report | דוח נגישות מפורט', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Site info
    elements.append(Paragraph(f'אתר נבדק: {last_audit_result["url"]}', normal_style))
    elements.append(Paragraph(f'תאריך: {last_audit_result["timestamp"]}', normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # WCAG Level summary
    elements.append(Paragraph('מידע על רמת WCAG', heading_style))
    elements.append(Paragraph(f'סוג האתר: {last_audit_result["wcag_level"]["site_type"]}', normal_style))
    elements.append(Paragraph(f'רמה נדרשת: {last_audit_result["wcag_level"]["required_level"]}', normal_style))
    elements.append(Paragraph(f'רמה שהושגה: {last_audit_result["wcag_level"]["achieved_label"]}', normal_style))
    elements.append(Paragraph(last_audit_result["wcag_level"]["achieved_description"], normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # WCAG Levels table
    elements.append(Paragraph('סטטוס עמידה ברמות WCAG', heading_style))
    wcag_data = [['Level', 'Status', 'Description']]
    for level, info in last_audit_result['wcag_level']['all_levels'].items():
        status = 'Pass' if info['passes'] else 'Fail'
        wcag_data.append([info['label'], status, info['description']])
    
    wcag_table = Table(wcag_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
    wcag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(wcag_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Issues summary
    elements.append(Paragraph('סיכום בעיות', heading_style))
    elements.append(Paragraph(f'סה"כ בעיות: {last_audit_result["total_issues"]}', normal_style))
    elements.append(Paragraph(f'קריטיות: {len(last_audit_result["issues"]["critical"])}', normal_style))
    elements.append(Paragraph(f'גבוהות: {len(last_audit_result["issues"]["high"])}', normal_style))
    elements.append(Paragraph(f'בינוניות: {len(last_audit_result["issues"]["medium"])}', normal_style))
    elements.append(Paragraph(f'נמוכות: {len(last_audit_result["issues"]["low"])}', normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed issues
    priorities = [
        ('critical', 'בעיות קריטיות'),
        ('high', 'בעיות בעדיפות גבוהה'),
        ('medium', 'בעיות בעדיפות בינונית'),
        ('low', 'בעיות בעדיפות נמוכה')
    ]
    
    for priority_key, priority_name in priorities:
        issues = last_audit_result['issues'][priority_key]
        if issues:
            elements.append(PageBreak())
            elements.append(Paragraph(f'{priority_name} ({len(issues)})', heading_style))
            elements.append(Spacer(1, 0.2*inch))
            
            for i, issue in enumerate(issues, 1):
                elements.append(Paragraph(f'{i}. {issue["type"]}', normal_style))
                elements.append(Paragraph(f'   {issue["details"]}', normal_style))
                
                if 'count' in issue:
                    elements.append(Paragraph(f'   מספר מופעים: {issue["count"]}', normal_style))
                
                if 'examples' in issue and issue['examples']:
                    elements.append(Paragraph('   דוגמאות:', normal_style))
                    for example in issue['examples'][:5]:
                        elements.append(Paragraph(f'      - {example[:100]}...', normal_style))
                
                elements.append(Spacer(1, 0.1*inch))
    
    # Statistics
    elements.append(PageBreak())
    elements.append(Paragraph('סטטיסטיקות מפורטות', heading_style))
    elements.append(Paragraph(f'תמונות: {last_audit_result["stats"]["total_images"]} סה"כ, '
                             f'{last_audit_result["stats"]["images_without_alt"]} ללא alt', normal_style))
    elements.append(Paragraph(f'קישורים: {last_audit_result["stats"]["total_links"]} סה"כ, '
                             f'{last_audit_result["stats"]["unclear_links"]} לא ברורים', normal_style))
    elements.append(Paragraph(f'שדות טופס: {last_audit_result["stats"]["total_forms"]} סה"כ, '
                             f'{last_audit_result["stats"]["forms_without_labels"]} ללא labels', normal_style))
    elements.append(Paragraph(f'כפתורים: {last_audit_result["stats"]["total_buttons"]} סה"כ, '
                             f'{last_audit_result["stats"]["buttons_without_text"]} ללא טקסט', normal_style))
    elements.append(Paragraph(f'טבלאות: {last_audit_result["stats"]["total_tables"]} סה"כ, '
                             f'{last_audit_result["stats"]["tables_without_headers"]} ללא headers', normal_style))
    elements.append(Paragraph(f'כותרות H1: {last_audit_result["stats"]["h1_count"]}', normal_style))
    elements.append(Paragraph(f'שפת הדף: {"כן" if last_audit_result["stats"]["has_lang"] else "לא"}', normal_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF from buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=accessibility-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.pdf'
    
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
