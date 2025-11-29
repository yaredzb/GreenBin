from fpdf import FPDF
import datetime
import os
import tempfile
from typing import List, Dict

class GreenBinReport(FPDF):
    """Simplified Professional PDF Report Generator"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Custom header"""
        self.set_fill_color(16, 185, 129)  # Green
        self.rect(0, 0, 210, 25, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 15, 'GreenBin Sustainability Report', 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)
        self.ln(15)
        
    def footer(self):
        """Custom footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} | Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def section_title(self, title):
        """Styled section title"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(16, 185, 129)
        self.cell(0, 8, title.upper(), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def metric_box(self, label, value, x_pos, y_pos, width=45):
        """Simple metric box"""
        self.set_xy(x_pos, y_pos)
        self.set_fill_color(245, 247, 250)
        self.rect(x_pos, y_pos, width, 20, 'F')
        self.rect(x_pos, y_pos, width, 20)
        
        self.set_font('Arial', 'B', 14)
        self.set_xy(x_pos, y_pos + 4)
        self.cell(width, 6, str(value), 0, 0, 'C')
        
        self.set_font('Arial', '', 8)
        self.set_text_color(100, 100, 100)
        self.set_xy(x_pos, y_pos + 11)
        self.cell(width, 5, label, 0, 0, 'C')
        self.set_text_color(0, 0, 0)

def calculate_metrics(bins: List, history: List, facilities: List) -> Dict:
    """Calculate key metrics"""
    total_collections = len([h for h in history if h.get('status') == 'Collected'])
    co2_saved = total_collections * 2.5
    
    request_collections = len([h for h in history if h.get('source') == 'request'])
    total_requests = request_collections + len([h for h in history if h.get('status') == 'Collected'])
    efficiency = (total_collections / total_requests * 100) if total_requests > 0 else 100.0
    
    return {
        'total_bins': len(bins),
        'total_collections': total_collections,
        'efficiency': efficiency,
        'co2_saved': co2_saved,
        'critical_bins': len([b for b in bins if b.fill_level >= 80]),
        'recycling_rate': (len([h for h in history if h.get('type') == 'Recyclable']) / total_collections * 100) if total_collections > 0 else 0.0
    }

def generate_professional_report(bins: List, history: List, facilities: List) -> str:
    """Generate a simplified one-page professional report"""
    metrics = calculate_metrics(bins, history, facilities)
    
    pdf = GreenBinReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Key Metrics Row
    y_start = pdf.get_y()
    pdf.metric_box('Total Bins', metrics['total_bins'], 10, y_start)
    pdf.metric_box('Collections', metrics['total_collections'], 58, y_start)
    pdf.metric_box('Efficiency', f"{metrics['efficiency']:.1f}%", 106, y_start)
    pdf.metric_box('CO2 Saved', f"{metrics['co2_saved']:.1f} kg", 154, y_start)
    
    pdf.set_y(y_start + 30)
    
    # 2. Facility Status
    pdf.section_title('Facility Status')
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(40, 7, 'Location', 1)
    pdf.cell(30, 7, 'Capacity', 1, 0, 'C')
    pdf.cell(30, 7, 'Efficiency', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    for f in sorted(facilities, key=lambda x: x.efficiency, reverse=True)[:5]:
        pdf.cell(40, 7, f"{f.lat:.2f}, {f.lon:.2f}", 1)
        pdf.cell(30, 7, str(f.capacity), 1, 0, 'C')
        pdf.cell(30, 7, f"{f.efficiency:.1f}%", 1, 1, 'C')
    
    pdf.ln(8)
    
    # 3. Recent Activity
    pdf.section_title('Recent Collections')
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(30, 7, 'Bin ID', 1)
    pdf.cell(40, 7, 'Type', 1)
    pdf.cell(50, 7, 'Time', 1, 1)
    
    pdf.set_font('Arial', '', 9)
    recent = [h for h in history if h.get('status') == 'Collected'][-5:]
    if not recent:
        pdf.cell(0, 7, 'No recent activity', 1, 1, 'C')
    else:
        for h in recent:
            pdf.cell(30, 7, str(h.get('bin_id')), 1)
            pdf.cell(40, 7, str(h.get('type')), 1)
            pdf.cell(50, 7, str(h.get('timestamp')), 1, 1)
            
    pdf.ln(8)
    
    # 4. Recommendations
    pdf.section_title('Recommendations')
    pdf.set_font('Arial', '', 10)
    
    recs = []
    if metrics['critical_bins'] > 0:
        recs.append(f"- Dispatch required for {metrics['critical_bins']} critical bins (>=80% full).")
    if metrics['efficiency'] < 90:
        recs.append("- Optimize collection routes to improve efficiency.")
    if metrics['recycling_rate'] < 30:
        recs.append(f"- Promote recycling (current rate: {metrics['recycling_rate']:.1f}%).")
    if not recs:
        recs.append("- System operating normally.")
        
    for r in recs:
        pdf.cell(0, 6, r, 0, 1)

    # Save
    temp_dir = tempfile.gettempdir()
    filename = f"GreenBin_Summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(temp_dir, filename)
    pdf.output(filepath)
    
    return filepath
