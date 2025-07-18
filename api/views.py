from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import MedicalReport
from .serializers import MedicalReportSerializer
from django.contrib.auth.models import User
from .utils import call_deepseek_ai
from .utils import format_table_for_ai
import requests
import time
import os
from .firebase_config import firebase_admin
from firebase_admin import auth
from firebase_admin import auth as firebase_auth
from rest_framework.authentication import get_authorization_header
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# 🔹 Azure OCR Call
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")
print("🔐 AZURE_ENDPOINT =", os.getenv("AZURE_ENDPOINT"))

def call_azure_ocr(file):
    url = f"{AZURE_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Content-Type": "application/octet-stream"
    }

    file.seek(0)
    response = requests.post(url, headers=headers, data=file.read())

    if response.status_code != 202:
        raise Exception("Azure OCR failed", response.text)

    result_url = response.headers["operation-location"]

    # Polling
    for _ in range(10):
        time.sleep(1)
        result = requests.get(result_url, headers={"Ocp-Apim-Subscription-Key": AZURE_KEY})
        result_json = result.json()
        if result_json.get("status") == "succeeded":
            return result_json  # NOT just analyzeResult
    raise Exception("Azure OCR polling timed out")


# 🔹 NEW: Extract full text from OCR result
def extract_full_text(ocr_json):
    """Extract all text content from OCR result as fallback"""
    analyze_result = ocr_json.get("analyzeResult", {})
    
    # Try to get content from paragraphs first (best for text reports)
    paragraphs = analyze_result.get("paragraphs", [])
    if paragraphs:
        full_text = "\n".join([p.get("content", "") for p in paragraphs])
        return full_text.strip()
    
    # Fallback to pages content
    pages = analyze_result.get("pages", [])
    full_text = ""
    for page in pages:
        lines = page.get("lines", [])
        page_text = "\n".join([line.get("content", "") for line in lines])
        full_text += page_text + "\n"
    
    return full_text.strip()


# 🔹 Enhanced Extract Tables and Date with fallback
def extract_tables_and_date(ocr_json):
    result = {}
    analyze_result = ocr_json.get("analyzeResult", {})

    # Extract Tables
    tables = analyze_result.get("tables", [])
    parsed_tables = []
    for table in tables:
        rows = table.get("rowCount", 0)
        cols = table.get("columnCount", 0)
        cells = table.get("cells", [])
        data_grid = [["" for _ in range(cols)] for _ in range(rows)]

        for cell in cells:
            row = cell.get("rowIndex")
            col = cell.get("columnIndex")
            text = cell.get("content", "")
            data_grid[row][col] = text

        parsed_tables.append(data_grid)

    result["tables"] = parsed_tables

    # Extract Report Date
    report_date = None
    for kv in analyze_result.get("keyValuePairs", []):
        key = kv.get("key", {}).get("content", "").lower()
        val = kv.get("value", {}).get("content", "")
        if "date" in key and val:
            report_date = val
            break
    
    # If no date found in key-value pairs, try to extract from full text
    if not report_date:
        full_text = extract_full_text(ocr_json)
        # Simple regex to find date patterns
        import re
        date_patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',     # YYYY/MM/DD
            r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b'  # DD Mon YYYY
        ]
        for pattern in date_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                report_date = match.group()
                break
    
    result["report_date"] = report_date
    
    # 🔹 NEW: Add full text as fallback
    result["full_text"] = extract_full_text(ocr_json)
    
    return result


# 🔹 NEW: Enhanced AI prompt formatting
def create_ai_prompt(cleaned_data, report_type):
    """Create appropriate AI prompt based on report content"""
    
    tables = cleaned_data.get("tables", [])
    full_text = cleaned_data.get("full_text", "")
    report_date = cleaned_data.get("report_date", "")
    
    print(f"🧠 Creating AI prompt for report type: {report_type}")
    print(f"📊 Tables found: {len(tables)}")
    print(f"📄 Full text length: {len(full_text)} characters")
    
    # Check if we have meaningful tabular data
    has_good_tables = False
    if tables:
        for table in tables:
            # Check if table has meaningful content (not just empty cells)
            meaningful_cells = 0
            for row in table:
                for cell in row:
                    if cell.strip() and len(cell.strip()) > 2:
                        meaningful_cells += 1
            
            if meaningful_cells > 4:  # At least 4 meaningful cells
                has_good_tables = True
                break
    
    # Choose prompt strategy based on content
    if has_good_tables:
        print("✅ Using table-based prompt")
        # Use existing table formatting logic
        return format_table_for_ai(cleaned_data)
    
    elif full_text and len(full_text) > 100:  # Substantial text content
        print("✅ Using text-based prompt")
        
        # Determine report type from content or parameter
        if any(keyword in full_text.lower() for keyword in ['ct scan', 'mri', 'ultrasound', 'x-ray', 'imaging']):
            prompt = f"""You are a medical assistant. The following is a medical imaging report. Please provide a clear, simple summary that a patient can understand. Focus on the key findings and their significance:

Date: {report_date if report_date else 'Not specified'}
Report Type: {report_type}

--- MEDICAL REPORT ---
{full_text}
--- END REPORT ---

Please provide:
1. A brief overview of what was examined
2. Key findings in simple language
3. Any recommendations or follow-up needed
4. Overall assessment

Keep the language simple and avoid complex medical jargon."""

        elif any(keyword in full_text.lower() for keyword in ['blood', 'lab', 'test', 'result', 'value']):
            prompt = f"""You are a medical assistant. The following is a laboratory report. Please provide a clear, simple summary that a patient can understand:

Date: {report_date if report_date else 'Not specified'}
Report Type: {report_type}

--- LAB REPORT ---
{full_text}
--- END REPORT ---

Please provide:
1. Summary of tests performed
2. Key findings and what they mean
3. Any values that are outside normal ranges
4. Overall health assessment based on results

Keep the language simple and avoid complex medical jargon."""

        else:
            prompt = f"""You are a medical assistant. Please analyze the following medical report and provide a clear, simple summary that a patient can understand:

Date: {report_date if report_date else 'Not specified'}
Report Type: {report_type}

--- MEDICAL REPORT ---
{full_text}
--- END REPORT ---

Please provide:
1. Overview of the report
2. Key findings in simple language
3. Any recommendations
4. Overall assessment

Keep the language simple and avoid complex medical jargon."""
        
        return prompt
    
    else:
        print("❌ Insufficient data for AI prompt")
        return f"""I was unable to properly extract the content from this {report_type} report. The document may be unclear or in a format that's difficult to process. Please ensure the document is clear and try uploading again, or consult with your healthcare provider for interpretation."""


# 🔹 Upload View - CSRF EXEMPT
@method_decorator(csrf_exempt, name='dispatch')
class UploadLabReport(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print("🔍 Raw request data:", request.data)

        token_header = get_authorization_header(request).split()
        if not token_header or token_header[0].lower() != b'bearer':
            return Response({"error": "Authorization header missing or invalid."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            id_token = token_header[1].decode()
            decoded_token = firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
            uid = decoded_token['uid']

            # 🔐 Fetch secure info from Firebase
            firebase_user = firebase_auth.get_user(uid)
            email = firebase_user.email
            name = firebase_user.display_name or "Anonymous"

        except Exception as e:
            return Response({"error": "Invalid Firebase token", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Create or update the user
        user, created = User.objects.get_or_create(username=uid, defaults={
            'email': email,
            'first_name': name.split(" ")[0],
            'last_name': " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
        })

        if not created:
            user.email = email
            user.first_name = name.split(" ")[0]
            user.last_name = " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
            user.save()
       
        # Now you can continue with report processing

        #proceed with report saving
        file = request.data.get("original_file")
        report_type = request.data.get("report_type")

        if not file or not report_type:
            return Response({"error": "File and report_type are required."}, status=400)

        # Step 1: Save file to DB (first)
        report = MedicalReport.objects.create(
            user=user,
            report_type=report_type,
            original_file=file
        )

        try:
            # Step 2: OCR Call + Cleanup
            print("🚀 Starting OCR processing...")
            ocr_json = call_azure_ocr(file)
            print("✅ OCR processing completed successfully.")

            cleaned_data = extract_tables_and_date(ocr_json)
            print("🧹 Cleaned data keys:", list(cleaned_data.keys()))
            print("📊 Tables found:", len(cleaned_data.get("tables", [])))
            print("📄 Full text length:", len(cleaned_data.get("full_text", "")))

            # 🔹 NEW: Use enhanced AI prompt creation
            ai_prompt = create_ai_prompt(cleaned_data, report_type)
            print("📋 AI prompt preview (first 200 chars):", ai_prompt[:200] + "..." if len(ai_prompt) > 200 else ai_prompt)

            from datetime import datetime
            raw_date = cleaned_data.get("report_date", "")
            print("📅 Raw date:", raw_date)
            parsed_date = None
            if raw_date:
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                    try:
                        parsed_date = datetime.strptime(raw_date, fmt).date()
                        print("✅ Parsed date:", parsed_date)
                        break
                    except Exception as e:
                        print(f"❌ Date parse failed for format {fmt}: {e}")
            
            # Step 3: Save extracted data to model
            report.extracted_data = cleaned_data
            report.ai_prompt_preview = ai_prompt[:1000]  # Store first 1000 chars for preview
            report.report_date = parsed_date
            report.save()
            print("✅ Report saved after OCR.")

            try:
                # 🔹 ENHANCED: Call AI service with better error handling
                print("🤖 Calling AI service...")
                ai_summary = call_deepseek_ai(ai_prompt)
                
                if not ai_summary or len(ai_summary.strip()) < 50:
                    print("⚠️ AI returned short/empty response, using fallback")
                    ai_summary = f"Report processed successfully. Please consult with your healthcare provider for detailed interpretation of this {report_type} report."
                
                report.ai_summary = ai_summary
                report.save()
                print("✅ AI summary saved to report.")
                
            except Exception as ai_err:
                print("❌ AI call failed:", ai_err)
                ai_summary = f"Report uploaded successfully, but AI analysis failed. Please consult with your healthcare provider for interpretation of this {report_type} report."
                report.ai_summary = ai_summary
                report.save()
            
            return Response({
                "message": "Report uploaded and processed successfully.", 
                "ai_summary": ai_summary,
                "report_id": report.id
            }, status=201)
            
        except Exception as e:
            print("🔥 Outer exception:", e)
            return Response({"error": str(e)}, status=500)

# user ki saari reports ko fetch karne ke liye
# views.py

@method_decorator(csrf_exempt, name='dispatch')
class ReportListAPIView(APIView):
    def get(self, request):
        print("🔍 === DEBUG: ReportListAPIView called ===")
        print("📥 Headers:", dict(request.headers))
        print("🔑 Authorization header raw:", request.headers.get('Authorization'))
        
        token_header = get_authorization_header(request).split()
        print("🔑 Token header split:", token_header)
        
        if not token_header or token_header[0].lower() != b'bearer':
            print("❌ Authorization header missing or invalid")
            print("Token header:", token_header)
            return Response({"error": "Authorization header missing or invalid."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            id_token = token_header[1].decode()
            print("🎫 ID Token (first 50 chars):", id_token[:50] + "...")
            
            decoded = firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
            print("✅ Firebase token decoded successfully")
            print("👤 Decoded token keys:", list(decoded.keys()))
            
            uid = decoded['uid']
            print("🆔 UID:", uid)
            
            # 🔐 Fetch secure info from Firebase
            firebase_user = firebase_auth.get_user(uid)
            email = firebase_user.email
            name = firebase_user.display_name or "Anonymous"
            
            # ✅ Create or get the user (same as in UploadLabReport)
            user, created = User.objects.get_or_create(username=uid, defaults={
                'email': email,
                'first_name': name.split(" ")[0],
                'last_name': " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
            })

            if not created:
                user.email = email
                user.first_name = name.split(" ")[0]
                user.last_name = " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
                user.save()
            
            print("👤 User found/created:", user.username, user.email)
            
        except Exception as e:
            print("❌ Firebase token verification failed:", str(e))
            print("❌ Exception type:", type(e).__name__)
            import traceback
            traceback.print_exc()
            return Response({"error": "Invalid Firebase token", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        reports = MedicalReport.objects.filter(user=user).order_by('-report_date')
        print("📊 Found reports count:", reports.count())
        
        serializer = MedicalReportSerializer(reports, many=True)
        print("✅ Serialization successful")
        
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ReportDeleteView(APIView):
    def delete(self, request, pk):
        # Add Firebase authentication
        token_header = get_authorization_header(request).split()
        if not token_header or token_header[0].lower() != b'bearer':
            return Response({"error": "Authorization header missing or invalid."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            id_token = token_header[1].decode()
            decoded = firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
            uid = decoded['uid']
            user = User.objects.get(username=uid)
        except Exception as e:
            return Response({"error": "Invalid Firebase token", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Only allow users to delete their own reports
            report = MedicalReport.objects.get(pk=pk, user=user)
            report.delete()
            return Response({"message": "Report deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except MedicalReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class FirebaseLoginView(APIView):
    def post(self, request):
        id_token = request.data.get('token')
        name = request.data.get('name')
        email = request.data.get('email')

        if not id_token:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = auth.verify_id_token(id_token)
            print("🔥 Firebase Decoded Token:", decoded_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name')

            # Try to find existing user or create a new one
            user, created = User.objects.get_or_create(username=uid, defaults={
                'email': email,
                'first_name': name.split(" ")[0],
                'last_name': " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
            })
            if not created:
                user.email = email
                user.first_name = name.split(" ")[0]
                user.last_name = " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else ""
                user.save()
            return Response({'message': 'User authenticated', 'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.first_name
            }})

        except Exception as e:
            print("Firebase auth error:", e)
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)