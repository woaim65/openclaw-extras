# openclaw-extras

> openclaw 的增强工具包，让 AI 助手更贴合自己的使用习惯。

---

## 功能一览

### 💾 session-auto-save（自动保存）

**能做什么：** 每隔15分钟自动把当前对话存档到 `memory/autosave/`，不需要 `/new` 或 `/reset`。

**为什么有用：** 
- 对话超过几小时回头找内容，直接翻存档，不用往上翻几百条
- 系统压缩或重启后，silence 期的内容不会丢失
- 每次存档只保留最近20条对话，保持文件精简

**原理：** 直接读取 session JSONL 文件，不走 API，不泄露数据。

---

### ⚖️ task-risk-rater（风险分级）

**能做什么：** 执行任务前先过一遍风险分级：

| 等级 | 触发条件 | 动作 |
|------|---------|------|
| 🔴 HIGH | 删除文件、强制 push、暴露密码 | 先上报，等确认 |
| 🟡 MEDIUM | 修改配置、安装 skill、git push | 执行后汇报 |
| 🟢 LOW | 读文件、查询状态 | 直接执行 |

**为什么有用：** 每次操作前多一步判断，减少"删完了才说"的风险。

---

### 🔍 health-check（多维健康检查）

**能做什么：** 一键检查5个维度：

```
Gateway  → gateway 进程是否活着
Cron     → 定时任务有没有跳过
Memory   → 今日日记、核心文件是否完整
Disk     → 磁盘空间够不够
Proactive → 这段时间有没有主动做事
```

**为什么有用：** 一个脚本看全局，不用一个个检查。

---

### 🔄 commit-scanner（官方动态跟踪）

**能做什么：** 每两天自动扫描官方 OpenClaw commits，判断哪些值得跟、哪些是闭源收紧。

**为什么有用：** 官方升级时主动判断，不被动等通知。

---

## 适用场景

- 想让 AI 更主动、更系统化
- 想追踪 AI 的思考和行动历史
- 想在官方闭源收紧时保持自主控制
- 想把增强工具分享给其他人

---

## 安装方式

```bash
# session-auto-save
cp -r hooks/session-auto-save ~/.openclaw/hooks/
systemctl --user restart openclaw-gateway

# scripts（直接运行）
python3 scripts/task-risk-rater.py "删除某个目录"
python3 scripts/health-check.py
```

---

## 背景

这是[真真的 openclaw 配置](https://github.com/woaim65/openclaw)（fork 官方最新版）的增强工具集。

核心思路：
- **地理决定论**：所有增强都在本地跑，不依赖外部 API
- **Privacy first**：数据不出内网
- **Evolution**：官方闭源收紧的部分，自己同步维护

---

## 状态

活跃维护中。

有问题或想法 → 开 issue
