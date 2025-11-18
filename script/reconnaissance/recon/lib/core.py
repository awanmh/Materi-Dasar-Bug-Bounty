import asyncio
import os
from collections import defaultdict
from datetime import datetime
from lib.utils import ProgressBar, load_template_file, C
from lib.database import Database
from lib.auth import SessionManager

class EngineContext:
    """Satu objek untuk menyimpan SEMUA status pemindaian v12.0"""
    
    def __init__(self, session, pyppeteer_browser, args):
        self.session = session
        self.pyppeteer_browser = pyppeteer_browser
        self.args = args
        
        # UI/UX
        self.C = C()
        self.progress_bar = ProgressBar(args.silent)
        self.logger = self.progress_bar.log
        
        # Kontrol Konkurensi
        self.concurrency = args.concurrency # <-- PERBAIKAN DI SINI
        self.semaphore = asyncio.Semaphore(args.concurrency)
        
        # Komponen Inti
        self.db = Database(os.path.join(args.output, "recon.db"), self.C)
        self.auth = SessionManager(self)
        self.evidence = EvidenceCollector(self.C)
        
        # Kontrol State
        self.crawl_queue = asyncio.Queue()
        self.processed_urls = set()
        self.waf_detected = set()
        self.session_valid = True
        self.dynamic_vars = {}
        
        # Signatures & Templat
        self.tech_signatures = load_template_file(args.tech_signatures)
        self.js_patterns = load_template_file(args.js_patterns)
        self.waf_signatures = load_template_file(args.waf_signatures)
        self.templates = [] # Akan diisi oleh main()
        
        # Penyimpanan Hasil (Cache)
        self.results = {
            'subdomains': set(),
            'live_hosts': set(), 'endpoints': defaultdict(set),
            'found_params_get': defaultdict(set), 'found_params_post': defaultdict(dict)
        }
        
        # Data Filter
        self.filter_status_codes = set(args.filter_status or [])
        self.filter_content_lengths = set(args.filter_size or [])

class EvidenceCollector:
    """(Tidak berubah dari v10.1)"""
    def __init__(self, C_class):
        self.evidence_store = defaultdict(list)
        self.lock = asyncio.Lock()
        self.C = C_class

    async def add_evidence(self, finding_type, location, evidence, severity="INFO"):
        entry = {
            'type': finding_type, 'location': location, 'evidence': evidence,
            'severity': severity, 'timestamp': datetime.now().isoformat(), 'verified': True
        }
        sev_color = self.C.G
        if severity.lower() == 'medium': sev_color = self.C.Y
        elif severity.lower() == 'high': sev_color = self.C.R
        elif severity.lower() == 'critical': sev_color = self.C.BR
        evidence['color_severity'] = f"{sev_color}{severity.upper()}{self.C.W}"
        async with self.lock:
            self.evidence_store[finding_type].append(entry)
        return entry