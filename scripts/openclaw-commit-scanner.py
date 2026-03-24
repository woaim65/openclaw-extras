#!/usr/bin/env python3
"""
OpenClaw 官方 commit 扫描器
每两天运行一次，自动检查官方仓库的新 commits
"""
import subprocess
import json
from datetime import datetime, timedelta

OFFICIAL_REPO = "openclaw/openclaw"
WORKSPACE_REPO = "/home/oz/.openclaw/workspace"
FORK_BRANCH = "main"  # woaim65/openclaw 的 main 分支
STATE_FILE = "/home/oz/.openclaw/logs/commit-scan-state.json"

def ensure_upstream():
    """确保 upstream remote 存在"""
    try:
        subprocess.run(["git", "remote", "get-url", "upstream"], 
                      capture_output=True, cwd=WORKSPACE_REPO, timeout=5)
        print("upstream remote 已存在")
    except:
        print("添加 upstream remote...")
        subprocess.run(
            ["git", "remote", "add", "upstream", "https://github.com/openclaw/openclaw.git"],
            capture_output=True, cwd=WORKSPACE_REPO, timeout=10
        )
        # fetch 一次
        subprocess.run(["git", "fetch", "upstream"], 
                      capture_output=True, cwd=WORKSPACE_REPO, timeout=30)

def get_official_commits(days=2):
    """获取官方最近 N 天的 commits"""
    ensure_upstream()
    cmd = [
        "git", "log",
        f"--since={days} days ago",
        "--format=%H|%ai|%s|%ae",
        "upstream/main"
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_REPO, timeout=30)
        if r.returncode != 0:
            print(f"git log 失败: {r.stderr}")
            return []
        commits = []
        for line in r.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "subject": parts[2],
                    "author": parts[3]
                })
        return commits
    except Exception as e:
        print(f"获取 commits 失败: {e}")
        return []

def check_fork_sync_status():
    """检查 fork 是否同步到最新官方"""
    try:
        ensure_upstream()
        subprocess.run(["git", "fetch", "upstream"], capture_output=True, cwd=WORKSPACE_REPO, timeout=30)
        # 检查 fork 和官方的差距
        r = subprocess.run(
            ["git", "log", "--oneline", "HEAD..upstream/main"],
            capture_output=True, text=True, cwd=WORKSPACE_REPO, timeout=10
        )
        ahead = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
        return ahead
    except Exception as e:
        print(f"同步检查失败: {e}")
        return -1

def generate_report(commits, sync_gap):
    """生成报告"""
    report = []
    report.append(f"=== OpenClaw Commit Scan Report ===")
    report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"最近 commits: {len(commits)} 个")
    report.append(f"Fork 落后官方: {sync_gap} commits")
    report.append("")
    
    if commits:
        report.append("值得关注的 commits:")
        for c in commits[:10]:
            report.append(f"  - [{c['date'][:10]}] {c['subject']}")
            report.append(f"    {c['hash'][:8]} by {c['author']}")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("开始扫描 OpenClaw 官方 commits...")
    commits = get_official_commits(days=2)
    sync_gap = check_fork_sync_status()
    report = generate_report(commits, sync_gap)
    print(report)
    
    # 写日志
    log_file = "/home/oz/.openclaw/logs/commit-scan.log"
    with open(log_file, "a") as f:
        f.write(f"\n{'='*50}\n{report}\n")
    
    # 判断是否需要自主行动
    if sync_gap > 20:
        print(f"\n⚠️ Fork 落后官方 {sync_gap} commits，建议手动同步")
    elif commits:
        print(f"\n📋 发现 {len(commits)} 个新 commits，待 docker 奇兵验证")
    else:
        print("\n✅ 无新 commits，一切正常")
