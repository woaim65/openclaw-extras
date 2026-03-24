#!/usr/bin/env python3
"""
任务风险分级器
给定任务描述，输出风险等级和推荐动作

风险等级：
  LOW    → 自动执行
  MEDIUM → 执行后汇报
  HIGH   → 先上报，等确认

规则（非LLM，基于关键词规则）：
"""

RISK_KEYWORDS = {
    "HIGH": [
        "删除", "销毁", "毁灭", "rm ", "trash", "drop",
        "git push -f", "force push", "--force",
        "开放", "暴露", "expose", "泄露",
        "密码", "secret", "token", "credential",
        "账单", "支付", "charge", "billing",
        "重启", "shutdown", "halt",
    ],
    "MEDIUM": [
        "修改", "更新", "edit", "patch", "update",
        "安装", "install", "npm install",
        "创建", "文件", "write", "touch",
        "git commit", "git add", "git push",
        "发送", "消息", "message", "notify",
        "cron", "schedule",
    ],
}

ACTION_MAP = {
    "HIGH": "REPORT_FIRST",
    "MEDIUM": "EXECUTE_AND_REPORT", 
    "LOW": "AUTO_EXECUTE",
}

def rate(task_text: str) -> dict:
    task_lower = task_text.lower()
    
    # HIGH check
    for kw in RISK_KEYWORDS["HIGH"]:
        if kw.lower() in task_lower:
            return {"risk": "HIGH", "action": ACTION_MAP["HIGH"], "keyword": kw}
    
    # MEDIUM check
    for kw in RISK_KEYWORDS["MEDIUM"]:
        if kw.lower() in task_lower:
            return {"risk": "MEDIUM", "action": ACTION_MAP["MEDIUM"], "keyword": kw}
    
    return {"risk": "LOW", "action": ACTION_MAP["LOW"], "keyword": None}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        result = rate(task)
        print(f"{result['risk']} | {result['action']} | keyword={result['keyword']}")
    else:
        print("Usage: python3 task-risk-rater.py <task description>")
