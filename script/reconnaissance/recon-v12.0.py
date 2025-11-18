#!/usr/bin/env python3
"""
  ▄████████    ▄██████▄     ▄████████  ▄██████▄   ███    █▄
  ███    ███   ███    ███   ███    ███ ███    ███  ███    ███
  ███    █▀    ███    ███   ███    █▀  ███    ███  ███    ███
  ███          ███    ███  ▄███▄▄▄     ███    ███  ███    ███
  ███        ▀███████████ ▀▀███▀▀▀   ▀███████████  ███    ███
  ███    █▄    ███    ███   ███    █▄  ███    ███  ███    ███
  ███    ███   ███    ███   ███    ███ ███    ███  ███    ███
  ████████▀    ███    █▀    ██████████ ███    █▀   ████████▀
                 [v12.2 - Filename Fix Edition]
"""

import asyncio
import aiohttp
import time
import sys
import os
import json
import argparse
import random
from datetime import datetime
import logging
from urllib.parse import urlparse # <-- PERBAIKAN V12.2: Impor baru

try:
    from pyppeteer import launch
    from aiosqlite import connect
    from tqdm.asyncio import tqdm_asyncio
    import aiodns
    import yaml
    from lxml import etree
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Dependensi lengkap diperlukan.", file=sys.stderr)
    print("[!] Jalankan: pip install pyppeteer aiosqlite tqdm aiohttp aiodns PyYAML lxml beautifulsoup4", file=sys.stderr)
    print("[!] Jalankan juga: pyppeteer-install", file=sys.stderr)
    sys.exit(1)

# Impor dari library kustom Anda
from lib.core import EngineContext
from lib.discovery import SubdomainEnumerator, HostVerifier, WebCrawler
from lib.verification import TemplateEngine
from lib.utils import load_wordlist_from_file, load_template_file, C 

C_INSTANCE = C()

def print_warning():
    print(f"""
    {C_INSTANCE.Y}┌────────────────────────────────────────────────────────────┐
    │                     ⚠️  PROFESSIONAL USE ONLY                 │
    ├────────────────────────────────────────────────────────────┤
    │  This tool runs custom templates. You are responsible for   │
    │  the templates you load. Use only with explicit permission. │
    └────────────────────────────────────────────────────────────┘{C_INSTANCE.W}
    """)

def display_banner(ctx):
    args = ctx.args
    C = ctx.C
    header_count = f"SET ({len(args.header)})" if args.header else 'None'
    
    banner = f"""
    {C.BC}┌────────────────────────────────────────────────────────────┐
    │                                                            │
    │         🔍  RECONNAISSANCE FRAMEWORK v12.2 (Advanced)        │
    │            YAML Support, Regex/CSS/XPath Engine            │
    │                                                            │
    └────────────────────────────────────────────────────────────┘{C.W}
    
    {C.BG}[+] Target:{C.W}           {args.domain}
    {C.BG}[+] Output:{C.W}           {args.output}
    {C.BG}[+] Concurrency:{C.W}      {args.concurrency}
    {C.BG}[+] Mode:{C.W}             {"Headless (Smart)" if args.headless else "HTTP (Fast)"}
    {C.BG}[+] Recursive:{C.W}        {args.recursive}
    
    {C.BC}[+] Sources:{C.W}
    │   {C.C}Templates:{C.W}       {args.templates} ({C.Y}{len(ctx.templates)} loaded{C.W})
    │   {C.C}Wordlists:{C.W}       {args.subdomain_wordlist}, {args.directory_wordlist}
    
    {C.BC}[+] Authentication:{C.W}
    │   {C.C}Cookie:{C.W}           {"SET" if args.cookie else 'None'}
    │   {C.C}Headers:{C.W}          {header_count}
    │   {C.C}Auth Check:{C.W}       {args.auth_check_url or 'None'}
    
    {C.BC}[+] Time:{C.W}             {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    print(banner)

def generate_evidence_report(ctx):
    C = ctx.C
    print(f"\n{C.BG}[FINAL]{C.W} 📄 {C.BC}EVIDENCE REPORT{C.W}")
    print(f"{C.BC}┌────────────────────────────────────────────────────────────┐{C.W}")
    
    report = {
        'metadata': {
            'target': ctx.args.domain, 'scan_date': datetime.now().isoformat(),
            'version': '12.2', 'waf_detected': list(ctx.waf_detected)
        },
        'summary': {
            'live_hosts': len(ctx.results['live_hosts']),
            'endpoints_found': sum(len(v) for v in ctx.results['endpoints'].values()),
            'params_get_found': sum(len(v) for v in ctx.results['found_params_get'].values()),
            'params_post_found': sum(len(v) for v in ctx.results['found_params_post'].values()),
            'verified_issues': sum(len(v) for v in ctx.evidence.evidence_store.values())
        },
        'data': {
            'live_hosts': list(ctx.results['live_hosts']),
            'endpoints': {k: list(v) for k, v in ctx.results['endpoints'].items()},
            'parameters_get': {k: list(v) for k, v in ctx.results['found_params_get'].items()},
            'parameters_post': {k: {f: list(p) for f, p in v.items()} for k, v in ctx.results['found_params_post'].items()},
            'evidence': dict(ctx.evidence.evidence_store)
        }
    }
    
    print(f"  {C.BC}📋 EXECUTIVE SUMMARY{C.W}")
    print(f"  {C.C}──────────────────────────────────{C.W}")
    print(f"  {C.C}🎯 Target:{C.W}         {report['metadata']['target']}")
    print(f"  {C.C}🛡️  WAF Detected:{C.W}   {report['metadata']['waf_detected'] or 'None'}")
    print(f"  {C.C}⚡ Live Hosts:{C.W}     {report['summary']['live_hosts']}")
    print(f"  {C.C}📁 Endpoints:{C.W}      {report['summary']['endpoints_found']}")
    print(f"  {C.C}🔡 GET Params:{C.W}     {report['summary']['params_get_found']} | {C.C}POST Params:{C.W} {report['summary']['params_post_found']}")
    print(f"  {C.BM}🔥 Verified Issues:{C.W} {report['summary']['verified_issues']}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # --- PERBAIKAN V12.2: Gunakan args.sanitized_domain ---
        filename = f"{ctx.args.output}/recon_report_{ctx.args.sanitized_domain}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  {C.G}💾 Laporan lengkap disimpan di: {filename}{C.W}")
    except Exception as e:
        print(f"  {C.R}[!] Gagal menyimpan laporan: {e}{C.W}")
        
    print(f"{C.BC}└────────────────────────────────────────────────────────────┘{C.W}")
    return report

async def main():
    parser = argparse.ArgumentParser(
        description=f'{C_INSTANCE.BC}🔍 RECONNAISSANCE FRAMEWORK v12.2{C_INSTANCE.W}',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"{C_INSTANCE.Y}Example: python recon-v12.0.py example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 50{C_INSTANCE.W}"
    )
    
    core_args = parser.add_argument_group('Core Arguments')
    core_args.add_argument('domain', help='Target domain to analyze (e.g., example.com or localhost:3000)') # Diperbarui
    core_args.add_argument('-o', '--output', default=None, help='Output directory for results')
    core_args.add_argument('-c', '--concurrency', type=int, default=50, help='Number of concurrent tasks (default: 50)')
    core_args.add_argument('--silent', action='store_true', help='Disable most output, only show critical findings')
    core_args.add_argument('--resume', action='store_true', help='Resume scan from database')

    crawl_args = parser.add_argument_group('Crawler Arguments')
    crawl_args.add_argument('-r', '--recursive', action='store_true', help='Enable recursive crawling')
    crawl_args.add_argument('--headless', action='store_true', help='Use headless browser (Pyppeteer) for crawling')
    
    source_args = parser.add_argument_group('Source Arguments')
    source_args.add_argument('-t', '--templates', required=True, help='Path to templates folder (YAML/JSON)')
    source_args.add_argument('-sw', '--subdomain-wordlist', required=True, help='Path to subdomain wordlist file')
    source_args.add_argument('-dw', '--directory-wordlist', required=True, help='Path to directory/endpoint wordlist file')
    source_args.add_argument('-ts', '--tech-signatures', default='tech_signatures.json', help='Path to technology signatures JSON file')
    source_args.add_argument('-js', '--js-patterns', default='js_patterns.json', help='Path to JS regex patterns JSON file')
    source_args.add_argument('-ws', '--waf-signatures', default='waf_signatures.json', help='Path to WAF signatures JSON file')
    
    auth_args = parser.add_argument_group('Authentication & Session Arguments')
    auth_args.add_argument('-H', '--header', action='append', help='Add custom header (e.g., "Auth: ...")')
    auth_args.add_argument('-b', '--cookie', help='Add custom cookie string (e.g., "SESSION=...")')
    auth_args.add_argument('--login-url', help='URL untuk POST data login')
    auth_args.add_argument('--login-data', help='Data form login (e.g., "user=a&pass=b")')
    auth_args.add_argument('--auth-check-url', help='URL untuk mengecek validitas sesi')
    auth_args.add_argument('--auth-check-string', help='String yang MUNCUL jika sesi TIDAK VALID (logout)')
    
    evasion_args = parser.add_argument_group('Evasion & Filter Arguments')
    evasion_args.add_argument('-ua', '--user-agents', help='Path to file with User-Agents (one per line) for rotation')
    evasion_args.add_argument('-p', '--proxy', help='Set a single proxy (e.g., "http://127.0.0.1:8080")')
    evasion_args.add_argument('--filter-status', type=int, nargs='+', help='Filter (ignore) responses with these status codes')
    evasion_args.add_argument('--filter-size', type=int, nargs='+', help='Filter (ignore) responses with these content lengths')

    args = parser.parse_args()
    
    if not args.output:
        args.output = f"recon_{args.domain}_{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(args.output, exist_ok=True)

    # --- PERBAIKAN V12.2: Membersihkan domain input ---
    domain_input = args.domain
    # 1. Hapus skema http/https jika ada
    if domain_input.startswith(('http://', 'https://')):
        parsed_url = urlparse(domain_input)
        args.domain = parsed_url.netloc # Mengubah "http://localhost:3000" -> "localhost:3000"
    
    # 2. Buat nama file yang aman dari args.domain yang (mungkin) sudah bersih
    safe_name = args.domain.replace(':', '_').replace('.', '_')
    args.sanitized_domain = safe_name
    # --- AKHIR PERBAIKAN ---

    if not args.silent: print_warning()
    start_time = time.time()
    
    custom_headers = {}
    user_agents_list = load_wordlist_from_file(args.user_agents) if args.user_agents else []
    custom_headers["User-Agent"] = random.choice(user_agents_list) if user_agents_list else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if args.header:
        for h in args.header:
            if ':' in h: key, value = h.split(':', 1); custom_headers[key.strip()] = value.strip()
    custom_cookies = {}
    if args.cookie:
        for c in args.cookie.split(';'):
            if '=' in c: key, value = c.split('=', 1); custom_cookies[key.strip()] = value.strip()

    pyppeteer_browser = None
    try:
        if args.headless:
            if not args.silent: print(f"{C_INSTANCE.Y}[+]{C_INSTANCE.W} Meluncurkan browser headless (Pyppeteer)...")
            pyppeteer_browser = await launch(headless=True, args=['--no-sandbox', '--disable-gpu'])

        async with aiohttp.ClientSession(
            headers=custom_headers, cookies=custom_cookies, proxy=args.proxy
        ) as session:
            
            ctx = EngineContext(session, pyppeteer_browser, args)
            await ctx.db.connect()
            
            if not os.path.isdir(args.templates):
                ctx.logger(f"  {C_INSTANCE.R}[!] FATAL: Path templat '{args.templates}' bukan direktori.{C_INSTANCE.W}"); sys.exit(1)
            for filename in os.listdir(args.templates):
                if filename.endswith(('.json', '.yaml', '.yml')):
                    tpl = load_template_file(os.path.join(args.templates, filename))
                    if tpl: ctx.templates.append(tpl)
            if not ctx.templates:
                ctx.logger(f"  {C_INSTANCE.Y}[!] Peringatan: Tidak ada templat .yaml/.json yang dimuat.{C_INSTANCE.W}");
            
            # Inisialisasi Modul
            subdomain_enum = SubdomainEnumerator(args.domain)
            host_verifier = HostVerifier()
            web_crawler = WebCrawler(ctx)
            template_engine = TemplateEngine(ctx)
            
            if not args.silent: display_banner(ctx)
            
            if args.login_url and not args.resume:
                if not await ctx.auth.login():
                    ctx.logger(f"  {C_INSTANCE.R}[!] Login awal gagal. Keluar.{C_INSTANCE.W}"); sys.exit(1)
            
            if args.resume:
                ctx.logger(f"{C_INSTANCE.BG}[+]{C_INSTANCE.W} Melanjutkan sesi dari database...")
                ctx.results['live_hosts'] = await ctx.db.get_live_hosts()
                ctx.results['endpoints'] = await ctx.db.get_endpoints()
                ctx.results['found_params_get'] = await ctx.db.get_get_params()
                ctx.results['found_params_post'] = await ctx.db.get_post_params()
                ctx.logger(f"  {C_INSTANCE.G}[+]{C_INSTANCE.W} Dimuat ulang: {len(ctx.results['live_hosts'])} host.")
            
            # --- Menjalankan Alur Pemindaian v12.2 ---
            
            if not args.resume:
                print(f"\n{C_INSTANCE.BY}[>>> PHASE 1: SUBDOMAIN DISCOVERY <<<]{C_INSTANCE.W}")
                sub_wordlist = load_wordlist_from_file(args.subdomain_wordlist)
                if sub_wordlist: 
                    await subdomain_enum.check_wildcard(ctx)
                    ctx.results['subdomains'] = await subdomain_enum.enumerate(ctx, sub_wordlist)
                
                print(f"\n{C_INSTANCE.BY}[>>> PHASE 2: HOST VERIFICATION <<<]{C_INSTANCE.W}")
                hosts_to_check = ctx.results['subdomains'] | {args.domain}
                ctx.results['live_hosts'] = await host_verifier.verify(ctx, hosts_to_check)

                print(f"\n{C_INSTANCE.BY}[>>> PHASE 3: WEB CRAWLING & DISCOVERY <<<]{C_INSTANCE.W}")
                dir_wordlist = load_wordlist_from_file(args.directory_wordlist)
                await web_crawler.crawl(dir_wordlist, resume=False)
            
            print(f"\n{C_INSTANCE.BY}[>>> PHASE 4: TEMPLATE-BASED ASSESSMENT <<<]{C_INSTANCE.W}")
            await template_engine.run_assessment()
            
            generate_evidence_report(ctx)
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n{C_INSTANCE.BG}✅ RECONNAISSANCE COMPLETED{C_INSTANCE.W}")
            print(f"{C_INSTANCE.G}⏱️  Durasi Total: {duration:.2f} detik{C_INSTANCE.W}")
            
    except KeyboardInterrupt: print(f"\n{C_INSTANCE.R}[!] Operasi dihentikan oleh pengguna.{C_INSTANCE.W}")
    except Exception as e:
        print(f"\n{C_INSTANCE.R}[!] Terjadi error fatal: {e}{C_INSTANCE.W}", file=sys.stderr); logging.exception("Fatal error")
    finally:
        if 'ctx' in locals() and ctx.db: await ctx.db.close()
        if pyppeteer_browser: await pyppeteer_browser.close()

if __name__ == "__main__":
    asyncio.run(main())