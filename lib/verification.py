import asyncio
import logging
import re
import random
import string
from urllib.parse import quote, urljoin
from lib.utils import load_wordlist_from_file, get_text_from_bytes, extract_with_json, extract_with_xpath, extract_with_css

# SSL Context
import ssl
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

class TemplateEngine:
    """Mesin Verifikasi v12.1: Chaining Logic Diperbaiki"""
    
    def __init__(self, ctx):
        self.ctx = ctx

    async def run_assessment(self):
        """Menjalankan SEMUA templat pada target yang sesuai"""
        
        await self.ctx.auth.ensure_session_valid()
        if not self.ctx.session_valid and (self.ctx.args.auth_check_url or self.ctx.args.cookie):
            self.ctx.logger(f"  {self.ctx.C.R}[!] Pemindaian kerentanan dihentikan karena sesi tidak valid.{self.ctx.C.W}")
            return

        tasks = []
        for template in self.ctx.templates:
            target_type = template.get('target', 'host')
            
            if target_type == 'host':
                for host_url in self.ctx.results['live_hosts']:
                    tasks.append(self._run_template(template, {'base_url': host_url}))
            elif target_type == 'params_get':
                for base_url, params in self.ctx.results['found_params_get'].items():
                    for param_name in params:
                        tasks.append(self._run_template(template, {
                            'base_url': base_url,
                            'param_name': param_name
                        }))
            # TODO: params_post
        
        if not tasks:
            self.ctx.logger(f"  {self.ctx.C.Y}[!] Tidak ada target verifikasi kerentanan.{self.ctx.C.W}"); return

        self.ctx.logger(f"  {self.ctx.C.G}[+]{self.ctx.C.W} Memulai {len(tasks)} tugas verifikasi templat...")
        await self.ctx.progress_bar.create(len(tasks), "Verifying Vulns")
        await asyncio.gather(*tasks)
        await self.ctx.progress_bar.close()

    async def _run_template(self, template, target_data):
        """
        --- PERBAIKAN V12.1 ---
        Menjalankan satu templat (berpotensi multi-request)
        HANYA melaporkan jika SEMUA request di chain berhasil.
        """
        if not self.ctx.session_valid: return
        
        async with self.ctx.semaphore:
            if not self.ctx.session_valid: return
            
            self.ctx.dynamic_vars = {} 
            all_requests_succeeded = True
            
            try:
                for i, req in enumerate(template['requests']):
                    
                    # Logika untuk menjalankan request (tunggal atau payload file)
                    match_success = False
                    if 'payload_file' in req:
                        payload_list = load_wordlist_from_file(req['payload_file'])
                        for payload_item in payload_list:
                            if not self.ctx.session_valid: break
                            await self.ctx.auth.ensure_session_valid()
                            
                            if await self._execute_request(template, req, target_data, payload_override=payload_item):
                                match_success = True # Jika SATU payload berhasil, request ini dianggap sukses
                                break # Hentikan brute-force pada temuan pertama
                    else:
                        match_success = await self._execute_request(template, req, target_data, payload_override=None)
                    
                    # --- Logika Chaining ---
                    if not match_success:
                        all_requests_succeeded = False
                        break # Hentikan chain jika satu request gagal
                
                # --- Logika Pelaporan (Dipindah ke sini) ---
                if all_requests_succeeded:
                    info = template['info']
                    location = target_data.get('base_url', '').split('?')[0]
                    evidence_data = {'template_id': template['id'], 'target': target_data}
                    
                    entry = await self.ctx.evidence.add_evidence(
                        template['id'], location, evidence_data, info['severity']
                    )
                    color_sev = entry['evidence']['color_severity']
                    self.ctx.logger(f"    {self.ctx.C.BR}🔥 [TEMUAN: {color_sev}{self.ctx.C.BR}]{self.ctx.C.W} {info['name']} {self.ctx.C.Y}@{self.ctx.C.W} {location}")
                        
            except Exception as e:
                logging.error(f"Error menjalankan templat {template['id']}: {e}")
            
            await self.ctx.progress_bar.update()

    def _replace_placeholders(self, text, payload, target_data):
        """(Tidak berubah dari v11)"""
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        text = text.replace('{{base_url}}', target_data.get('base_url', ''))
        text = text.replace('{{param_name}}', target_data.get('param_name', ''))
        text = text.replace('{{payload}}', quote(payload.replace('{{rand}}', rand_str)))
        for key, value in self.ctx.dynamic_vars.items():
            text = text.replace(f"{{{{{key}}}}}", value)
        text = text.replace('{{rand}}', rand_str)
        return text, rand_str

    async def _execute_request(self, template, req, target_data, payload_override=None):
        """
        --- PERBAIKAN V12.1 ---
        Mengirim satu request HTTP dan mengembalikan True/False (apakah match).
        """
        method = req.get('method', 'GET').upper()
        payload = payload_override if payload_override is not None else req.get('payload', '')
        
        path, rand_str = self._replace_placeholders(req['path'], payload, target_data)
        data = None
        
        if method == 'POST':
            body_str = req.get('body', '')
            body_str, _ = self._replace_placeholders(body_str, payload, target_data)
            try:
                data = dict(x.split('=') for x in body_str.split('&'))
            except ValueError:
                data = body_str

        try:
            if method == 'GET':
                async with self.ctx.session.get(path, ssl=SSL_CONTEXT, timeout=10) as response:
                    return await self._process_response(req, response, rand_str)
            elif method == 'POST':
                async with self.ctx.session.post(path, data=data, ssl=SSL_CONTEXT, timeout=10) as response:
                    return await self._process_response(req, response, rand_str)
        except Exception as e:
            logging.warning(f"Request {template['id']} ke {path} gagal: {e}")
            return False # Gagal = tidak match

    async def _process_response(self, req, response, rand_str):
        """
        --- PERBAIKAN V12.1 ---
        Memeriksa matchers dan extractors, mengembalikan status match.
        TIDAK LAGI MELAPORKAN TEMUAN.
        """
        raw_body = await response.read()
        headers = {k.lower(): str(v) for k, v in response.headers.items()}
        body_str = None
        
        match_success, body_str = self._check_matchers(req, response, raw_body, headers, rand_str, body_str)
        
        # Ekstraktor HANYA dijalankan jika matcher berhasil
        if match_success and 'extractors' in req:
            if body_str is None: body_str = get_text_from_bytes(raw_body)
            self._run_extractors(req['extractors'], body_str, headers)

        return match_success

    def _run_extractors(self, extractors, body_str, headers):
        """(Tidak berubah dari v12.0)"""
        for extractor in extractors:
            ext_type = extractor['type']
            ext_name = extractor['name']
            extracted_value = None
            try:
                if ext_type == 'regex':
                    part = extractor.get('part', 'body').lower()
                    target_content = body_str if part == 'body' else headers.get(part, '')
                    match = re.search(extractor['regex'], target_content)
                    if match: extracted_value = match.group(1)
                elif ext_type == 'json':
                    extracted_value = extract_with_json(body_str, extractor['jsonpath'])
                elif ext_type == 'xpath':
                    extracted_value = extract_with_xpath(body_str, extractor['xpath'])
                elif ext_type == 'css':
                    extracted_value = extract_with_css(body_str, extractor['css_selector'], extractor['attribute'])
                
                if extracted_value:
                    self.ctx.dynamic_vars[ext_name] = extracted_value
                    self.ctx.logger(f"      {self.ctx.C.M}[VAR]{self.ctx.C.W} Ekstrak '{ext_name}' = '{extracted_value[:30]}...'")
            except Exception as e:
                logging.warning(f"Extractor {ext_type} '{ext_name}' gagal: {e}")

    def _check_matchers(self, req, response, raw_body, headers, rand_str, body_str):
        """(Tidak berubah dari v12.0)"""
        if 'matchers' not in req:
            return False, body_str 
        matchers_condition = req.get('matchers_condition', 'and').lower()
        all_match_success = True
        one_match_success = False
        for matcher in req['matchers']:
            match_found = False
            m_type = matcher['type']
            if m_type == 'status':
                if response.status == matcher['status']:
                    match_found = True
            elif m_type in ('word', 'regex'):
                if body_str is None: body_str = get_text_from_bytes(raw_body)
                part = matcher.get('part', 'body').lower()
                target_content = body_str if part == 'body' else headers.get(part, '')
                condition = matcher.get('condition', 'or').lower()
                patterns = matcher.get('words', []) if m_type == 'word' else matcher.get('regex', [])
                patterns = [p.replace('{{rand}}', rand_str) for p in patterns]
                if m_type == 'word':
                    if condition == 'or':
                        if any(word in target_content for word in patterns): match_found = True
                    else:
                        if all(word in target_content for word in patterns): match_found = True
                elif m_type == 'regex':
                    if condition == 'or':
                        if any(re.search(pattern, target_content) for pattern in patterns): match_found = True
                    else:
                        if all(re.search(pattern, target_content) for pattern in patterns): match_found = True
            elif m_type == 'binary':
                part = matcher.get('part', 'body').lower()
                if part != 'body': continue
                condition = matcher.get('condition', 'or').lower()
                hex_payloads = [bytes.fromhex(p) for p in matcher.get('hex_payloads', [])]
                if condition == 'or':
                    if any(payload in raw_body for payload in hex_payloads): match_found = True
                else:
                    if all(payload in raw_body for payload in hex_payloads): match_found = True
            elif m_type == 'header':
                part = matcher.get('part', '').lower()
                if part and part in headers:
                    if any(word in headers[part] for word in matcher['words']):
                        match_found = True
            if match_found: one_match_success = True
            if not match_found: all_match_success = False
        if matchers_condition == 'and':
            return all_match_success, body_str
        elif matchers_condition == 'or':
            return one_match_success, body_str
        return False, body_str