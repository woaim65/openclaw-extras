#!/usr/bin/env python3
"""
多维健康度检查器
5个专项维度，每次heartbeat各自验证
"""
import os
import sqlite3
import subprocess
import time
import json
from pathlib import Path

HOME = Path.home()
WORKSPACE = Path("/home/oz/.openclaw/workspace")
CRON_LOG = HOME / ".openclaw" / "logs" / "cron-runs.jsonl"
MEMORY_DIR = HOME / ".openclaw" / "workspace" / "memory"
ONTOLOGY_DIR = HOME / ".openclaw" / "memory" / "ontology"

def check_gateway():
    """1. Gateway 进程"""
    try:
        r = subprocess.run(["openclaw", "gateway", "status"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return "OK", "Gateway 在线"
        return "FAIL", f"返回码 {r.returncode}"
    except Exception as e:
        return "FAIL", str(e)

def check_cron():
    """2. Cron 定时任务"""
    checks = []
    # 检查核心文件备份 cron
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
        crons = r.stdout
        if "backup-core-files" in crons:
            checks.append("✅ 核心文件备份 cron 存在")
        else:
            checks.append("❌ 核心文件备份 cron 缺失")
        if "telegram-wan-check" in crons:
            checks.append("✅ Telegram检查 cron 存在")
        else:
            checks.append("❌ Telegram检查 cron 缺失")
        if "clock-in-remind" in crons:
            checks.append("✅ 打卡提醒 cron 存在")
        else:
            checks.append("❌ 打卡提醒 cron 缺失")
    except Exception as e:
        checks.append(f"crontab读取失败: {e}")
    
    # 检查最近cron运行日志
    if CRON_LOG.exists():
        try:
            lines = CRON_LOG.read_text().strip().split("\n")
            if lines:
                last = json.loads(lines[-1])
                age = time.time() - last.get("time", 0)
                if age < 3600:
                    checks.append(f"✅ Cron最近运行 {int(age/60)}分钟前")
                else:
                    checks.append(f"⚠️ Cron上次运行 {int(age/3600)}小时前")
        except:
            checks.append("⚠️ Cron日志读取异常")
    else:
        checks.append("⚠️ 无Cron运行日志")
    
    return "OK" if all("❌" not in c for c in checks) else "WARN", "; ".join(checks)

def check_memory():
    """3. 记忆系统"""
    checks = []
    # 检查今日日记
    today = time.strftime("%Y-%m-%d")
    today_mem = MEMORY_DIR / f"{today}.md"
    if today_mem.exists():
        age = time.time() - today_mem.stat().st_mtime
        checks.append(f"✅ 今日日记存在 ({int(age/60)}分钟前更新)")
    else:
        checks.append(f"❌ 今日日记缺失")
    
    # 检查MEMORY.md
    mem_file = WORKSPACE / "MEMORY.md"
    if mem_file.exists():
        checks.append("✅ MEMORY.md 存在")
    else:
        checks.append("❌ MEMORY.md 缺失")
    
    # 检查核心文件哈希记录
    hash_file = HOME / ".openclaw" / "backups" / ".file_hashes.json"
    if hash_file.exists():
        checks.append("✅ 哈希记录存在")
    else:
        checks.append("⚠️ 无哈希记录（备份未运行过）")
    
    return "OK" if all(c.startswith("✅") for c in checks) else "WARN", "; ".join(checks)

def check_disk():
    """4. 磁盘空间"""
    try:
        r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = r.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            used_pct = int(parts[4].replace("%", ""))
            avail = parts[3]
            if used_pct < 80:
                return "OK", f"系统盘 使用{used_pct}%（剩余{avail}）"
            elif used_pct < 90:
                return "WARN", f"系统盘 使用{used_pct}%（紧张，剩余{avail}）"
            else:
                return "FAIL", f"系统盘 使用{used_pct}%（严重不足，剩余{avail}）"
    except Exception as e:
        return "FAIL", str(e)

def check_proactive():
    """5. 主动性 — 检查最近有没有主动汇报（基于今日日记最新条目时间）"""
    today = time.strftime("%Y-%m-%d")
    today_mem = MEMORY_DIR / f"{today}.md"
    if today_mem.exists():
        try:
            # 读最后修改时间
            mtime = today_mem.stat().st_mtime
            age = time.time() - mtime
            if age < 7200:  # 2小时内有活动
                return "OK", f"今日有主动记录（{int(age/60)}分钟前）"
            return "WARN", f"今日最后活动 {int(age/3600)}小时前"
        except:
            pass
    return "WARN", "今日无主动活动记录"

if __name__ == "__main__":
    print("=== 多维健康度检查 ===")
    checks = [
        ("Gateway", check_gateway),
        ("Cron", check_cron),
        ("Memory", check_memory),
        ("Disk", check_disk),
        ("Proactive", check_proactive),
    ]
    
    all_ok = True
    for name, fn in checks:
        status, msg = fn()
        icon = "🟢" if status == "OK" else ("🟡" if status == "WARN" else "🔴")
        print(f"{icon} {name}: {msg}")
        if status != "OK":
            all_ok = False
    
    print()
    print("=== 总评 ===")
    if all_ok:
        print("🟢 全部正常")
    else:
        print("🟡 部分异常，请查看上文")
