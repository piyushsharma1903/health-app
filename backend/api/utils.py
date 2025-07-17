import requests
import json
import os

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_ai(prompt):
    """Call DeepSeek AI API with the given prompt"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
        raise e

def format_table_for_ai(cleaned_data):
    """Format extracted data for AI analysis - Enhanced version"""
    
    tables = cleaned_data.get("tables", [])
    full_text = cleaned_data.get("full_text", "")
    report_date = cleaned_data.get("report_date", "")
    
    print(f"🔍 format_table_for_ai called:")
    print(f"  - Tables: {len(tables)}")
    print(f"  - Full text length: {len(full_text)}")
    print(f"  - Report date: {report_date}")
    
    if not tables and not full_text:
        print("❌ No tables or full text found")
        return "No medical data could be extracted from the report. Please ensure the document is clear and try again."
    
    # If we have tables, try to format them properly
    if tables:
        formatted_tables = []
        for i, table in enumerate(tables):
            if not table:  # Skip empty tables
                continue
                
            print(f"📊 Processing table {i+1}: {len(table)} rows")
            
            # Check if table has meaningful content
            meaningful_rows = []
            for row in table:
                if any(cell.strip() for cell in row):  # At least one non-empty cell
                    meaningful_rows.append(row)
            
            if len(meaningful_rows) < 2:  # Skip tables with less than 2 rows
                continue
            
            # Format table for AI
            table_text = f"Table {i+1}:\n"
            for row_idx, row in enumerate(meaningful_rows):
                # Clean up row data
                clean_row = [cell.strip() for cell in row if cell.strip()]
                if clean_row:
                    if row_idx == 0:  # Likely header
                        table_text += "Headers: " + " | ".join(clean_row) + "\n"
                    else:
                        table_text += "Row: " + " | ".join(clean_row) + "\n"
            
            formatted_tables.append(table_text)
        
        if formatted_tables:
            table_content = "\n".join(formatted_tables)
            
            prompt = f"""You are a medical assistant. Analyze the following laboratory report and provide a clear, simple summary that a patient can understand.

Report Date: {report_date if report_date else 'Not specified'}

--- LABORATORY DATA ---
{table_content}
--- END DATA ---

Please provide a patient-friendly summary that includes:
1. Overview of what tests were performed
2. Key findings - which values are normal, high, or low
3. What these results mean for the patient's health
4. Any recommendations or next steps

Use simple language and avoid complex medical jargon. Be specific about the actual values and reference ranges shown."""

            print(f"✅ Generated table-based prompt ({len(prompt)} chars)")
            return prompt
    
    # Fallback to full text if tables didn't work
    if full_text and len(full_text) > 50:
        print("🔄 Falling back to full text analysis")
        
        prompt = f"""You are a medical assistant. Analyze the following laboratory report and provide a clear, simple summary that a patient can understand.

Report Date: {report_date if report_date else 'Not specified'}

--- LABORATORY REPORT ---
{full_text}
--- END REPORT ---

Please provide a patient-friendly summary that includes:
1. Overview of what tests were performed
2. Key findings - which values are normal, high, or low
3. What these results mean for the patient's health
4. Any recommendations or next steps

Use simple language and avoid complex medical jargon. Be specific about the actual values and reference ranges shown."""

        print(f"✅ Generated text-based prompt ({len(prompt)} chars)")
        return prompt
    
    # Final fallback
    print("⚠️ Using final fallback prompt")
    return "The laboratory report could not be properly processed. Please ensure the document is clear and contains readable text or tables, then try uploading again."


# Additional utility function to help debug OCR results
def debug_ocr_extraction(ocr_json):
    """Debug function to understand what OCR extracted"""
    print("\n🔍 === OCR DEBUG INFO ===")
    
    analyze_result = ocr_json.get("analyzeResult", {})
    
    # Check tables
    tables = analyze_result.get("tables", [])
    print(f"📊 Tables found: {len(tables)}")
    
    for i, table in enumerate(tables):
        print(f"  Table {i+1}: {table.get('rowCount', 0)} rows x {table.get('columnCount', 0)} cols")
        cells = table.get("cells", [])
        print(f"    Sample cells: {[cell.get('content', '') for cell in cells[:5]]}")
    
    # Check paragraphs
    paragraphs = analyze_result.get("paragraphs", [])
    print(f"📝 Paragraphs found: {len(paragraphs)}")
    if paragraphs:
        print(f"  First paragraph: {paragraphs[0].get('content', '')[:100]}...")
    
    # Check key-value pairs
    kvs = analyze_result.get("keyValuePairs", [])
    print(f"🔑 Key-value pairs found: {len(kvs)}")
    if kvs:
        for kv in kvs[:3]:  # Show first 3
            key = kv.get("key", {}).get("content", "")
            value = kv.get("value", {}).get("content", "")
            print(f"  {key}: {value}")
    
    # Check pages
    pages = analyze_result.get("pages", [])
    print(f"📄 Pages found: {len(pages)}")
    if pages:
        lines = pages[0].get("lines", [])
        print(f"  First page lines: {len(lines)}")
        if lines:
            print(f"    First line: {lines[0].get('content', '')}")
    
    print("=== END DEBUG INFO ===\n")