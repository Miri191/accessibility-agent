import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re

class AccessibilityAgent:
    """Agent for checking website accessibility"""
    
    def __init__(self, url: str):
        self.url = url
        self.soup = None
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        # Statistics for WCAG calculation
        self.stats = {
            'total_images': 0,
            'images_without_alt': 0,
            'total_links': 0,
            'unclear_links': 0,
            'has_lang': False,
            'h1_count': 0,
            'total_forms': 0,
            'forms_without_labels': 0,
            'total_buttons': 0,
            'buttons_without_text': 0,
            'total_tables': 0,
            'tables_without_headers': 0,
            'elements_checked_for_contrast': 0,
            'low_contrast_elements': 0,
        }
    
    def detect_required_level(self):
        """Detect the required WCAG level based on website type"""
        url_lower = self.url.lower()
        
        # Government sites - AAA required
        if any(domain in url_lower for domain in ['.gov.', 'gov.il', 'משרד', 'ממשלת', 'government']):
            return {
                'required_level': 'level_aaa',
                'site_type': 'ממשלתי',
                'reason': 'אתרי ממשל נדרשים לעמוד ברמת נגישות מקסימלית (AAA)'
            }
        
        # Banking and financial sites - AA required
        elif any(domain in url_lower for domain in ['bank', 'בנק', 'leumi', 'hapoalim', 'mizrahi', 'discount', 'finance']):
            return {
                'required_level': 'level_aa',
                'site_type': 'בנקאות ופיננסים',
                'reason': 'אתרי בנקאות ופיננסים נדרשים לעמוד בתקן AA'
            }
        
        # Public services and health - AA required
        elif any(domain in url_lower for domain in ['health', 'בריאות', 'hospital', 'clinic', 'education', 'חינוך', 'university', 'אוניברסיטה']):
            return {
                'required_level': 'level_aa',
                'site_type': 'שירות ציבורי',
                'reason': 'שירותי בריאות וחינוך נדרשים לעמוד בתקן AA'
            }
        
        # E-commerce - A required
        elif any(domain in url_lower for domain in ['shop', 'store', 'cart', 'buy', 'קנייה']):
            return {
                'required_level': 'level_a',
                'site_type': 'מסחר אלקטרוני',
                'reason': 'אתרי מסחר מומלצים לעמוד לפחות ברמה A'
            }
        
        # Default - A recommended
        else:
            return {
                'required_level': 'level_a',
                'site_type': 'כללי',
                'reason': 'מומלץ לעמוד לפחות ברמת נגישות בסיסית (A)'
            }

    
    def fetch_page(self):
        """Navigate to page and fetch HTML"""
        try:
            print(f"Fetching page: {self.url}")
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'lxml')
            print("Page loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading page: {e}")
            return False
    
    def check_images_alt_text(self):
        """Check alt text for images"""
        print("\nChecking images alt text...")
        images = self.soup.find_all('img')
        images_without_alt = []
        
        for img in images:
            if not img.get('alt'):
                images_without_alt.append(img.get('src', 'unknown'))
        
        # Update statistics
        self.stats['total_images'] = len(images)
        self.stats['images_without_alt'] = len(images_without_alt)
        
        if images_without_alt:
            self.issues['high'].append({
                'type': 'Missing alt text',
                'count': len(images_without_alt),
                'details': f"Found {len(images_without_alt)} images without alt text out of {len(images)} total",
                'examples': images_without_alt[:3]
            })
        
        print(f"   Checked {len(images)} images")
        print(f"   {len(images_without_alt)} images without alt text")
    
    def check_headings_hierarchy(self):
        """Check headings hierarchy"""
        print("\nChecking headings hierarchy...")
        headings = []
        
        for level in range(1, 7):
            tags = self.soup.find_all(f'h{level}')
            for tag in tags:
                headings.append((level, tag.get_text(strip=True)[:50]))
        
        h1_tags = [h for h in headings if h[0] == 1]
        
        # Update statistics
        self.stats['h1_count'] = len(h1_tags)
        
        if not h1_tags:
            self.issues['critical'].append({
                'type': 'Missing h1',
                'details': 'Page does not contain h1 heading'
            })
            print("   No h1 found!")
        elif len(h1_tags) > 1:
            self.issues['medium'].append({
                'type': 'Multiple h1',
                'details': f'Found {len(h1_tags)} h1 headings. Recommended: 1.'
            })
            print(f"   Found {len(h1_tags)} h1 headings (recommended: 1)")
        else:
            print(f"   Found h1: {h1_tags[0][1]}")
        
        # Check for skipped heading levels
        if len(headings) > 1:
            prev_level = 0
            for level, text in headings:
                if prev_level > 0 and level > prev_level + 1:
                    self.issues['medium'].append({
                        'type': 'Skipped heading level',
                        'details': f'Heading hierarchy jumps from h{prev_level} to h{level}'
                    })
                    break
                prev_level = level
        
        print(f"   Total headings: {len(headings)}")
    
    def check_lang_attribute(self):
        """Check lang attribute"""
        print("\nChecking lang attribute...")
        html_tag = self.soup.find('html')
        
        # Update statistics
        self.stats['has_lang'] = bool(html_tag and html_tag.get('lang'))
        
        if not html_tag or not html_tag.get('lang'):
            self.issues['high'].append({
                'type': 'Missing lang attribute',
                'details': 'HTML tag does not contain language attribute'
            })
            print("   Missing lang attribute")
        else:
            lang = html_tag.get('lang')
            print(f"   Page language: {lang}")
    
    def check_links_text(self):
        """Check links without clear text"""
        print("\nChecking links text...")
        links = self.soup.find_all('a')
        problematic_links = []
        
        for link in links:
            text = link.get_text(strip=True)
            aria_label = link.get('aria-label', '')
            
            if not text and not aria_label:
                problematic_links.append(link.get('href', 'unknown'))
            elif text.lower() in ['click here', 'read more', 'לחץ כאן', 'קרא עוד']:
                problematic_links.append(f"{text} -> {link.get('href', '')}")
        
        # Update statistics
        self.stats['total_links'] = len(links)
        self.stats['unclear_links'] = len(problematic_links)
        
        if problematic_links:
            self.issues['medium'].append({
                'type': 'Unclear links',
                'count': len(problematic_links),
                'details': f"Found {len(problematic_links)} links without clear text",
                'examples': problematic_links[:5]
            })
        
        print(f"   Checked {len(links)} links")
        print(f"   {len(problematic_links)} links with issues")
    
    def check_form_labels(self):
        """Check form inputs have associated labels"""
        print("\nChecking form labels...")
        inputs = self.soup.find_all(['input', 'textarea', 'select'])
        inputs_without_labels = []
        
        for inp in inputs:
            input_type = inp.get('type', 'text')
            # Skip hidden and submit buttons
            if input_type in ['hidden', 'submit', 'button']:
                continue
            
            has_label = False
            input_id = inp.get('id')
            aria_label = inp.get('aria-label')
            aria_labelledby = inp.get('aria-labelledby')
            
            # Check for label element
            if input_id:
                label = self.soup.find('label', {'for': input_id})
                if label:
                    has_label = True
            
            # Check for ARIA labels
            if aria_label or aria_labelledby:
                has_label = True
            
            # Check if wrapped in label
            if inp.find_parent('label'):
                has_label = True
            
            if not has_label:
                inputs_without_labels.append(f"{inp.name} type='{input_type}'")
        
        self.stats['total_forms'] = len(inputs)
        self.stats['forms_without_labels'] = len(inputs_without_labels)
        
        if inputs_without_labels:
            self.issues['high'].append({
                'type': 'Form inputs without labels',
                'count': len(inputs_without_labels),
                'details': f"Found {len(inputs_without_labels)} form inputs without accessible labels",
                'examples': inputs_without_labels[:5]
            })
        
        print(f"   Checked {len(inputs)} form inputs")
        print(f"   {len(inputs_without_labels)} inputs without labels")
    
    def check_buttons(self):
        """Check buttons have accessible text"""
        print("\nChecking buttons...")
        buttons = self.soup.find_all(['button', 'input'])
        buttons_without_text = []
        
        for btn in buttons:
            if btn.name == 'input' and btn.get('type') not in ['button', 'submit', 'reset']:
                continue
            
            text = btn.get_text(strip=True)
            value = btn.get('value', '')
            aria_label = btn.get('aria-label', '')
            
            if not text and not value and not aria_label:
                buttons_without_text.append(str(btn)[:100])
        
        self.stats['total_buttons'] = len([b for b in buttons if b.name == 'button' or (b.name == 'input' and b.get('type') in ['button', 'submit', 'reset'])])
        self.stats['buttons_without_text'] = len(buttons_without_text)
        
        if buttons_without_text:
            self.issues['high'].append({
                'type': 'Buttons without accessible text',
                'count': len(buttons_without_text),
                'details': f"Found {len(buttons_without_text)} buttons without accessible text",
                'examples': buttons_without_text[:3]
            })
        
        print(f"   Checked {self.stats['total_buttons']} buttons")
        print(f"   {len(buttons_without_text)} buttons without text")
    
    def check_tables(self):
        """Check tables have proper headers"""
        print("\nChecking tables...")
        tables = self.soup.find_all('table')
        tables_without_headers = []
        
        for table in tables:
            has_headers = False
            
            # Check for <th> elements
            if table.find('th'):
                has_headers = True
            
            # Check for scope or headers attributes
            if not has_headers:
                for td in table.find_all('td'):
                    if td.get('scope') or td.get('headers'):
                        has_headers = True
                        break
            
            if not has_headers:
                tables_without_headers.append(str(table)[:100])
        
        self.stats['total_tables'] = len(tables)
        self.stats['tables_without_headers'] = len(tables_without_headers)
        
        if tables_without_headers:
            self.issues['medium'].append({
                'type': 'Tables without headers',
                'count': len(tables_without_headers),
                'details': f"Found {len(tables_without_headers)} tables without proper headers",
                'examples': tables_without_headers[:2]
            })
        
        print(f"   Checked {len(tables)} tables")
        print(f"   {len(tables_without_headers)} tables without headers")
    
    def check_aria_landmarks(self):
        """Check for ARIA landmarks"""
        print("\nChecking ARIA landmarks...")
        has_main = bool(self.soup.find(['main', None], {'role': 'main'}))
        has_nav = bool(self.soup.find(['nav', None], {'role': 'navigation'}))
        has_footer = bool(self.soup.find(['footer', None], {'role': 'contentinfo'}))
        
        missing_landmarks = []
        if not has_main:
            missing_landmarks.append('main')
        if not has_nav:
            missing_landmarks.append('navigation')
        if not has_footer:
            missing_landmarks.append('footer/contentinfo')
        
        if missing_landmarks:
            self.issues['low'].append({
                'type': 'Missing ARIA landmarks',
                'details': f"Missing landmarks: {', '.join(missing_landmarks)}. Landmarks help screen reader users navigate.",
                'count': len(missing_landmarks)
            })
        
        print(f"   Found landmarks: main={has_main}, nav={has_nav}, footer={has_footer}")
    
    def check_skip_links(self):
        """Check for skip to main content links"""
        print("\nChecking skip links...")
        # Look for skip links in the first few links
        first_links = self.soup.find_all('a', limit=5)
        has_skip_link = False
        
        for link in first_links:
            text = link.get_text(strip=True).lower()
            href = link.get('href', '')
            
            if any(phrase in text for phrase in ['skip', 'jump', 'דלג', 'קפוץ']) and href.startswith('#'):
                has_skip_link = True
                break
        
        if not has_skip_link:
            self.issues['low'].append({
                'type': 'Missing skip link',
                'details': 'No skip to main content link found. This helps keyboard users bypass repetitive navigation.'
            })
            print("   No skip link found")
        else:
            print("   Skip link found")
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return None
    
    def calculate_relative_luminance(self, rgb):
        """Calculate relative luminance for contrast ratio"""
        if not rgb:
            return None
        
        r, g, b = [x/255.0 for x in rgb]
        
        # Apply gamma correction
        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def check_color_contrast(self):
        """Check color contrast ratios (simplified version)"""
        print("\nChecking color contrast (basic check)...")
        
        # This is a simplified check - real implementation would need to parse CSS
        # We'll check inline styles and basic color attributes
        elements_with_colors = self.soup.find_all(style=re.compile(r'color|background'))
        low_contrast_count = 0
        
        # Note: Full contrast checking requires rendering and CSS parsing
        # This is a basic heuristic check
        print(f"   Note: Full contrast checking requires CSS parsing and rendering")
        print(f"   Performing basic inline style check only")
        print(f"   Found {len(elements_with_colors)} elements with inline color styles")
        
        if len(elements_with_colors) == 0:
            self.issues['low'].append({
                'type': 'Color contrast check limited',
                'details': 'Contrast checking is limited without CSS parsing. Consider using browser-based tools for comprehensive contrast analysis.'
            })
    
    def calculate_wcag_level(self):
        """Calculate WCAG conformance level based on criteria"""
        critical_count = len(self.issues['critical'])
        high_count = len(self.issues['high'])
        medium_count = len(self.issues['medium'])
        
        # Calculate percentages for Level AA
        images_without_alt_pct = 0
        if self.stats['total_images'] > 0:
            images_without_alt_pct = (self.stats['images_without_alt'] / self.stats['total_images']) * 100
        
        unclear_links_pct = 0
        if self.stats['total_links'] > 0:
            unclear_links_pct = (self.stats['unclear_links'] / self.stats['total_links']) * 100
        
        forms_without_labels_pct = 0
        if self.stats['total_forms'] > 0:
            forms_without_labels_pct = (self.stats['forms_without_labels'] / self.stats['total_forms']) * 100
        
        # Level A requirements (basic)
        level_a_requirements = {
            'has_lang': self.stats['has_lang'],
            'has_h1': self.stats['h1_count'] >= 1,
            'all_images_have_alt': self.stats['images_without_alt'] == 0,
            'all_links_clear': self.stats['unclear_links'] == 0,
            'all_forms_labeled': self.stats['forms_without_labels'] == 0,
            'all_buttons_labeled': self.stats['buttons_without_text'] == 0
        }
        
        # Check if meets Level A
        meets_level_a = all(level_a_requirements.values())
        
        # Level AA requirements (standard)
        level_aa_requirements = {
            'single_h1': self.stats['h1_count'] == 1,
            'low_alt_issues': images_without_alt_pct < 10,
            'low_link_issues': unclear_links_pct < 5,
            'low_form_issues': forms_without_labels_pct < 5,
            'tables_accessible': self.stats['tables_without_headers'] == 0 or self.stats['total_tables'] == 0
        }
        
        meets_level_aa = meets_level_a and all(level_aa_requirements.values())
        
        # Level AAA requirements (high)
        level_aaa_requirements = {
            'no_critical': critical_count == 0,
            'no_high': high_count == 0,
            'max_medium': medium_count <= 2
        }
        
        meets_level_aaa = meets_level_aa and all(level_aaa_requirements.values())
        
        # Detect required level for this site
        required_info = self.detect_required_level()
        
        # Determine actual achieved level
        if not meets_level_a:
            achieved_level = 'non_compliant'
            achieved_label = 'לא עומד בתקן'
            achieved_description = 'האתר לא עומד בדרישות הבסיסיות של WCAG Level A'
            achieved_color = '#dc2626'
        elif meets_level_aaa:
            achieved_level = 'level_aaa'
            achieved_label = 'Level AAA - מצוין'
            achieved_description = 'האתר עומד בסטנדרט הגבוה ביותר של נגישות'
            achieved_color = '#10b981'
        elif meets_level_aa:
            achieved_level = 'level_aa'
            achieved_label = 'Level AA - תקן'
            achieved_description = 'האתר עומד בתקן המקובל של WCAG'
            achieved_color = '#3b82f6'
        else:
            achieved_level = 'level_a'
            achieved_label = 'Level A - בסיסי'
            achieved_description = 'האתר עומד בדרישות הבסיסיות של WCAG'
            achieved_color = '#f59e0b'
        
        # Check if meets required level
        level_hierarchy = {'non_compliant': 0, 'level_a': 1, 'level_aa': 2, 'level_aaa': 3}
        meets_required = level_hierarchy.get(achieved_level, 0) >= level_hierarchy.get(required_info['required_level'], 0)
        
        return {
            'achieved_level': achieved_level,
            'achieved_label': achieved_label,
            'achieved_description': achieved_description,
            'achieved_color': achieved_color,
            'required_level': required_info['required_level'],
            'site_type': required_info['site_type'],
            'required_reason': required_info['reason'],
            'meets_required': meets_required,
            'all_levels': {
                'level_a': {
                    'passes': meets_level_a,
                    'label': 'Level A - בסיסי',
                    'description': 'דרישות נגישות בסיסיות'
                },
                'level_aa': {
                    'passes': meets_level_aa,
                    'label': 'Level AA - תקן',
                    'description': 'תקן נגישות מקובל'
                },
                'level_aaa': {
                    'passes': meets_level_aaa,
                    'label': 'Level AAA - מצוין',
                    'description': 'נגישות ברמה הגבוהה ביותר'
                }
            }
        }

    
    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*60)
        print("ACCESSIBILITY AUDIT REPORT")
        print("="*60)
        print(f"\nWebsite: {self.url}\n")
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("Great! No issues found in basic checks")
            return
        
        print(f"Found {total_issues} issues:\n")
        
        if self.issues['critical']:
            print("CRITICAL ISSUES:")
            for issue in self.issues['critical']:
                print(f"   - {issue['type']}")
                print(f"     {issue['details']}\n")
        
        if self.issues['high']:
            print("HIGH PRIORITY ISSUES:")
            for issue in self.issues['high']:
                print(f"   - {issue['type']}")
                print(f"     {issue['details']}")
                if 'examples' in issue:
                    print(f"     Examples: {issue['examples'][:2]}\n")
        
        if self.issues['medium']:
            print("MEDIUM PRIORITY ISSUES:")
            for issue in self.issues['medium']:
                print(f"   - {issue['type']}")
                print(f"     {issue['details']}\n")
        
        print("="*60)
    
    def run_audit(self):
        """Run all checks"""
        print("\nStarting accessibility audit...\n")
        
        if not self.fetch_page():
            return
        
        # Basic checks
        self.check_lang_attribute()
        self.check_headings_hierarchy()
        self.check_images_alt_text()
        self.check_links_text()
        
        # Form and interaction checks
        self.check_form_labels()
        self.check_buttons()
        self.check_tables()
        
        # Structure checks
        self.check_aria_landmarks()
        self.check_skip_links()
        
        # Visual checks (limited without CSS parsing)
        self.check_color_contrast()
        
        self.generate_report()


if __name__ == "__main__":
    print("Accessibility Audit Agent")
    print("="*60)
    
    url = input("\nEnter URL to check: ").strip()
    
    if not url:
        print("No URL provided")
        exit()
    
    agent = AccessibilityAgent(url)
    agent.run_audit()
