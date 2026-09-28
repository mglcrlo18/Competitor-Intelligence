"""
export_engine.py
Automated Board-Ready C-Suite Export Engine.
Produces UTF-8 with BOM (.csv), SpreadsheetML XML (.xls), and Executive Markdown (.md) memos.
"""
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

def generate_utf8_bom_csv(df: pd.DataFrame) -> bytes:
    """Generates CSV with UTF-8 BOM (\uFEFF) to guarantee Excel character encoding compatibility."""
    csv_str = df.to_csv(index=False, encoding="utf-8-sig")
    return csv_str.encode("utf-8-sig")

def generate_spreadsheetml_xls(sheets_data: Any, sheet_name: str = 'Risk Register') -> str:
    if isinstance(sheets_data, pd.DataFrame):
        sheets_data = {sheet_name: sheets_data}
    """
    Generates a native Microsoft SpreadsheetML 2003 XML (.xls) formatted workbook
    with multiple sheets, bold headers, and grid formatting.
    """
    xml = """<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <Styles>
  <Style ss:ID="Default" ss:Name="Normal">
   <Alignment ss:Vertical="Bottom"/>
   <Borders/>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#000000"/>
   <Interior/>
   <NumberFormat/>
   <Protection/>
  </Style>
  <Style ss:ID="Header">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>
   </Borders>
   <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="1"/>
   <Interior ss:Color="#0F1E3A" ss:Pattern="Solid"/>
  </Style>
 </Styles>
"""
    for sheet_name, df in sheets_data.items():
        clean_sheet_name = sheet_name[:31].replace(":", "_").replace("/", "_")
        xml += f' <Worksheet ss:Name="{clean_sheet_name}">\n  <Table>\n'
        
        # Headers
        xml += '   <Row>\n'
        for col in df.columns:
            xml += f'    <Cell ss:StyleID="Header"><Data ss:Type="String">{col}</Data></Cell>\n'
        xml += '   </Row>\n'
        
        # Rows
        for _, row in df.iterrows():
            xml += '   <Row>\n'
            for val in row:
                v_str = str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                xml += f'    <Cell><Data ss:Type="String">{v_str}</Data></Cell>\n'
            xml += '   </Row>\n'
            
        xml += '  </Table>\n </Worksheet>\n'
        
    xml += '</Workbook>'
    return xml

def generate_csuite_markdown_memo(competitor_name: str, kpis: Dict[str, Any] = None, erm_data: Dict[str, Any] = None, gaps: List[Dict[str, Any]] = None) -> str:
    if erm_data is None:
        try:
            from erm_engine import calculate_erm_threat_matrix
            erm_data = calculate_erm_threat_matrix(competitor_name)
        except Exception:
            erm_data = {}
    if gaps is None:
        try:
            from messaging_gap import get_marketing_reality_gaps
            gaps = get_marketing_reality_gaps(competitor_name)
        except Exception:
            gaps = []
    if kpis is None:
        kpis = {}
    """Generates an executive C-Suite Intelligence Briefing Memo formatted in Markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memo = f"""# EXECUTIVE INTELLIGENCE MEMO // COMPETITIVE RADAR
**SUBJECT:** Strategic Threat Analysis: {competitor_name} vs. GoNano Infrastructure  
**DATE:** {timestamp}  
**AUTHOR:** Corporate Strategy & Competitive Intelligence Unit  
**GOVERNING FRAMEWORK:** ISO 31000 & COSO Enterprise Risk Management (ERM)  

---

### 1. EXECUTIVE RISK DASHBOARD (CRO RATING)
* **Target Competitor:** {competitor_name}
* **Inherent Competitive Threat:** `{erm_data.get('inherent_threat_score', 'N/A')}/10.0` ({erm_data.get('inherent_threat_level', 'MODERATE')})
* **Control Moat Efficacy (GoNano):** `{erm_data.get('control_efficacy_score', 'N/A')}/10.0` ({erm_data.get('control_efficacy_level', 'STRONG')})
* **Residual Market Exposure:** `{erm_data.get('residual_threat_score', 'N/A')}/10.0` ({erm_data.get('residual_threat_level', 'LOW')})
* **Polarity-VaR (90-Day Downside Risk):** `{erm_data.get('polarity_var_90d', 'N/A')}%` potential market share slippage under unmitigated price pressure.

---

### 2. PRIMARY MARKET EXPOSURE & KEY INDICATORS (KCIs)
**Exposure Vector:** {erm_data.get('primary_exposure', 'General Market Competition')}  

**Forward-Looking Early Warning Triggers:**
"""
    for kci in erm_data.get("kcis", []):
        memo += f"- **[{kci.get('severity')}] {kci.get('indicator')}:** Threshold `{kci.get('threshold')}` -> Status: `{kci.get('status')}`\n"
        
    memo += f"""
---

### 3. REVERSE STRESS TESTING (RST)
**Catastrophic Scenario:** {erm_data.get('reverse_stress_scenario', 'Competitor captures exclusive retail/insurance distributor exclusivity.')}  
**Strategic Countermeasure:** {erm_data.get('contingency_mitigation', 'Amplify GoNano ASTM laboratory validation and 15-year warranty moat.')}

---

### 4. BRAND PROMISE VS. CUSTOMER REALITY (MARKETING GAP)
"""
    for g in gaps[:3]:
        memo += f"""
#### Claim vs. Reality: {g.get('claim_headline')}
* **Official Marketing Assertion:** \"{g.get('claim_quote')}\" (Source: {g.get('claim_source')})
* **Ground-Level Customer Reality:** \"{g.get('reality_quote')}\" (Source: {g.get('reality_source')})
* **Divergence Severity:** `{g.get('gap_severity')}` ({g.get('divergence_score')}% divergence index)
* **Strategic Exploitation for GoNano:** {g.get('strategic_takeaway')}
"""

    memo += """
---

### 5. STRATEGIC BOARD ACTION ITEMS
1. **Commercial Positioning:** Differentiate GoNano's permanent molecular nanotech from ephemeral bio-oil topical coatings in all dealer sales collateral.
2. **Insurance Alignment:** Present forensic laboratory reports to insurance adjusters proving Class 3/4 hail impact enhancement.
3. **Retail & Contractor Moat:** Protect key regional markets (US Sunbelt, Canada East) through exclusive contractor volume rebates.

**[END OF INTELLIGENCE BRIEF // STRICTLY CONFIDENTIAL]**
"""
    return memo
