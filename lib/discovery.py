import asyncio
import aiodns
import uuid
import re
import logging
from urllib.parse import urlparse, parse_qs, urljoin

# SSL Context
import ssl
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

class SubdomainEnumerator:
    def __init__(self, domain):
        self.domain = domain
        self.wildcard_ips = set()
        self.resolver = aiodns.DNSResolver()

    async def check_wildcard(self, ctx):
        ctx.logger(f"  {ctx.C.G}[+]{ctx.C.W} Mendeteksi DNS Wildcard...")
        test_subs = [f"{uuid.uuid4().hex[:8]}" for _ in range(3)]
        resolved_ips = set()
        for sub in test_subs:
            try:
                full_domain = f"{sub}.{self.domain}"
                answers = await self.resolver.query(full_domain, 'A')
                for answer in answers: resolved_ips.add(answer.host)
            except aiodns.error.DNSError: continue
        if len(resolved_ips) > 0:
            ctx.logger(f"  {ctx.C.Y}[!] DNS Wildcard terdeteksi. IP: {resolved_ips}{ctx.C.W}")
            self.wildcard_ips = resolved_ips
        else:
            ctx.logger(f"  {ctx.C.G}[+]{ctx.C.W} Tidak ada DNS Wildcard terdeteksi.")

    async def _check_subdomain_worker(self, ctx, subdomain):
        full_domain = f"{subdomain}.{self.domain}"
        async with ctx.semaphore:
            try:
                answers = await self.resolver.query(full_domain, 'A')
                ips = {answer.host for answer in answers}
                if ips == self.wildcard_ips: return None
                ctx.logger(f"    {ctx.C.G}✅ Ditemukan:{ctx.C.W} {full_domain} {ctx.C.Y}→{ctx.C.W} {', '.join(ips)}")
                return full_domain
            except aiodns.error.DNSError: return None
            except Exception as e: logging.error(f"Error DNS di {full_domain}: {e}"); return None

    async def enumerate(self, ctx, wordlist):
        tasks = [self._check_subdomain_worker(ctx, sub) for sub in wordlist]
        await ctx.progress_bar.create(len(tasks), "Subdomain")
        results = [await f for f in asyncio.as_completed(tasks)]
        await ctx.progress_bar.update(len(tasks))
        await ctx.progress_bar.close()
        # Simpan ke 'subdomains' BUKAN 'live_hosts'
        ctx.results['subdomains'] = {res for res in results if res}
        return ctx.results['subdomains']

class HostVerifier:
    """(Tidak berubah dari v10.1)"""
    async def _check_host_live_worker(self, ctx, host):
        async with ctx.semaphore:
            for protocol in ['https', 'http']:
                url = f"{protocol}://{host}"
                try:
                    async with ctx.session.get(url, ssl=SSL_CONTEXT, timeout=5) as response:
                        if response.status:
                            ctx.logger(f"    {ctx.C.C}[LIVE] {url}{ctx.C.W} (Status: {ctx.C.Y}{response.status}{ctx.C.W})")
                            await ctx.db.add_live_host(url)
                            return url
                except Exception: continue
            return None

    async def verify(self, ctx, hosts):
        tasks = [self._check_host_live_worker(ctx, host) for host in hosts]
        await ctx.progress_bar.create(len(tasks), "Host Verify")
        results = [await f for f in asyncio.as_completed(tasks)]
        await ctx.progress_bar.update(len(tasks))
        await ctx.progress_bar.close()
        return {res for res in results if res}

class WebCrawler:
    """(Tidak berubah dari v10.1)"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.REGEX_INPUTS = re.compile(r'<(?:input|textarea).*?name=["\'](.*?)["\']', re.IGNORECASE)
        self.REGEX_FORMS = re.compile(r'<form.*?action=["\'](.*?)["\'].*?method=["\']POST["\']', re.IGNORECASE)
        self.REGEX_LINKS = re.compile(r'<a.*?href=["\'](.*?)["\']', re.IGNORECASE)

    async def _parse_parameters_and_links(self, url, content):
        base_domain = urlparse(url).netloc
        params_in_url = parse_qs(urlparse(url).query).keys()
        if params_in_url:
            self.ctx.logger(f"      {self.ctx.C.M}[PARAM-GET]{self.ctx.C.W} Ditemukan di {url}: {self.ctx.C.Y}{', '.join(params_in_url)}{self.ctx.C.W}")
            for param in params_in_url: 
                await self.ctx.db.add_get_param(url, param)
                self.ctx.results['found_params_get'][url].add(param) # <-- PERBAIKAN V12.1
            
        forms = self.REGEX_FORMS.findall(content)
        for form_action in forms:
            form_url = urljoin(url, form_action)
            inputs = self.REGEX_INPUTS.findall(content)
            if inputs:
                self.ctx.logger(f"      {self.ctx.C.M}[PARAM-POST]{self.ctx.C.W} Ditemukan form di {form_url}: {self.ctx.C.Y}{', '.join(inputs)}{self.ctx.C.W}")
                for param in inputs: 
                    await self.ctx.db.add_post_param(form_url, param)
                    self.ctx.results['found_params_post'][form_url][form_action] = set(inputs) # <-- PERBAIKAN V12.1

        if self.ctx.args.recursive:
            links = self.REGEX_LINKS.findall(content)
            for link in links:
                new_url = urljoin(url, link.strip())
                new_domain = urlparse(new_url).netloc
                if new_domain == base_domain and new_url not in self.ctx.processed_urls:
                    if new_url.rstrip('/') not in self.ctx.processed_urls:
                        await self.ctx.crawl_queue.put(new_url)

    async def _analyze_js(self, url, content):
        self.ctx.logger(f"      {self.ctx.C.B}[JS]{self.ctx.C.W} Menganalisis {url}...")
        for pattern in self.ctx.js_patterns:
            try:
                found = re.findall(pattern, content)
                if found:
                    self.ctx.logger(f"    {self.ctx.C.BR}🔥 [EVIDENCE]{self.ctx.C.W} Potensi path ditemukan di {url}: {self.ctx.C.Y}{', '.join(found)}{self.ctx.C.W}")
                    await self.ctx.evidence.add_evidence('JS_ENDPOINT_DISCOVERY', url, {'pattern': pattern, 'found': list(set(found))}, 'INFO')
            except Exception: continue

    async def _crawl_worker(self):
        while True:
            try:
                url = await self.ctx.crawl_queue.get()
                await self.ctx.auth.ensure_session_valid()
                if not self.ctx.session_valid:
                    self.ctx.crawl_queue.task_done(); break 
                normalized_url = url.rstrip('/')
                if normalized_url in self.ctx.processed_urls:
                    self.ctx.crawl_queue.task_done(); await self.ctx.progress_bar.update(); continue
                self.ctx.processed_urls.add(normalized_url)
                async with self.ctx.semaphore:
                    if self.ctx.args.headless: await self._process_url_headless(normalized_url)
                    else: await self._process_url_http(normalized_url)
                self.ctx.crawl_queue.task_done(); await self.ctx.progress_bar.update()
            except Exception as e:
                logging.error(f"Error pada worker crawler: {e}")
                self.ctx.crawl_queue.task_done(); await self.ctx.progress_bar.update()

    async def _process_url_http(self, url):
        try:
            async with self.ctx.session.get(url, ssl=SSL_CONTEXT, timeout=10) as response:
                if response.status in [429, 403]:
                    self.ctx.logger(f"  {self.ctx.C.Y}[!] {response.status} terdeteksi di {url}. Menunggu 30d...{self.ctx.C.W}");
                    await asyncio.sleep(30); await self.ctx.crawl_queue.put(url); return
                content = await response.read(); content_length = len(content)
                if response.status in self.ctx.filter_status_codes: return
                if content_length in self.ctx.filter_content_lengths: return
                if response.status < 400:
                    status_emoji = f"{self.ctx.C.G}🟢{self.ctx.C.W}" if response.status == 200 else f"{self.ctx.C.Y}🟡{self.ctx.C.W}"
                    self.ctx.logger(f"    {status_emoji} [{response.status}] {url} [{self.ctx.C.Y}{content_length} bytes{self.ctx.C.W}] (HTTP)")
                    await self.ctx.db.add_endpoint(url, urlparse(url).netloc)
                    self.ctx.results['endpoints'][urlparse(url).netloc].add(url) # <-- PERBAIKAN V12.1
                content_type = response.headers.get('Content-Type', '')
                try: content_str = content.decode('utf-8')
                except UnicodeDecodeError: content_str = content.decode('latin-1', errors='ignore')
                if 'text/html' in content_type and response.status == 200:
                    await self._parse_parameters_and_links(url, content_str)
                elif ('javascript' in content_type or url.endswith('.js')) and response.status == 200:
                    await self._analyze_js(url, content_str)
        except Exception as e: logging.warning(f"Gagal memproses HTTP {url}: {e}")

    async def _process_url_headless(self, url):
        page = None
        try:
            page = await self.ctx.pyppeteer_browser.newPage()
            if self.ctx.args.cookie:
                for cookie in self.ctx.args.cookie.split(';'):
                    if '=' in cookie: key, value = cookie.split('=', 1); await page.setCookie({'name': key.strip(), 'value': value.strip(), 'url': url})
            response = await page.goto(url, {'timeout': 15000, 'waitUntil': 'networkidle2'})
            status = response.status
            if status in [429, 403]:
                self.ctx.logger(f"  {self.ctx.C.Y}[!] {status} terdeteksi di {url}. Menunggu 30d...{self.ctx.C.W}");
                await asyncio.sleep(30); await self.ctx.crawl_queue.put(url); return
            content = await page.content(); content_length = len(content)
            if status in self.ctx.filter_status_codes: return
            if content_length in self.ctx.filter_content_lengths: return
            if status < 400:
                status_emoji = f"{self.ctx.C.G}🟢{self.ctx.C.W}" if status == 200 else f"{self.ctx.C.Y}🟡{self.ctx.C.W}"
                self.ctx.logger(f"    {status_emoji} [{status}] {url} [{self.ctx.C.Y}{content_length} bytes{self.ctx.C.W}] ({self.ctx.C.M}Headless{self.ctx.C.W})")
                await self.ctx.db.add_endpoint(url, urlparse(url).netloc)
                self.ctx.results['endpoints'][urlparse(url).netloc].add(url) # <-- PERBAIKAN V12.1
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type and status == 200:
                await self._parse_parameters_and_links(url, content)
            elif ('javascript' in content_type or url.endswith('.js')) and status == 200:
                await self._analyze_js(url, content)
        except Exception as e: logging.warning(f"Gagal memproses Headless {url}: {e}")
        finally:
            if page: await page.close()

    async def crawl(self, wordlist, resume=False):
        if not resume:
            for host_url in self.ctx.results['live_hosts']:
                await self.ctx.crawl_queue.put(host_url)
            for host_url in self.ctx.results['live_hosts']:
                for path in wordlist:
                    await self.ctx.crawl_queue.put(f"{host_url.rstrip('/')}/{path.lstrip('/')}")
        qsize = self.ctx.crawl_queue.qsize()
        if qsize == 0: self.ctx.logger(f"  {self.ctx.C.Y}[+] Tidak ada item dalam antrian crawler.{self.ctx.C.W}"); return
        await self.ctx.progress_bar.create(qsize, "Crawling")
        workers = [asyncio.create_task(self._crawl_worker()) for _ in range(self.ctx.concurrency)]
        await self.ctx.crawl_queue.join()
        for w in workers: w.cancel()
        await self.ctx.progress_bar.close()