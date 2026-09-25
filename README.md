# dirsearchx — dirsearch 三界面驱动（GUI / CLI）

围绕一份 **未修改** 的 dirsearch（放入 `vendor/`）做桌面 GUI 与命令行透传。
零第三方依赖：GUI 走标准库 tkinter，dirsearch 本体经子进程驱动。

## 功能

- **极简主屏**：目标 URL + 一键任务 + 常用参数快捷 + 运行控制 + 流式日志
- **一键任务**（10 个预设）：快速探测 / 后台配置 / Web 页面 / 管理后台 / 全量深度 / 备份文件 / 爬虫发现 / 限速礼貌扫 / JSON 报表 / 认证爆破
- **专家面板**：按 dirsearch `--help-all` 分 9 组、约 100 项全选项（布尔=复选框，取值=复选框+输入）
- **结果表**：自动解析 `[HH:MM:SS] STATUS - SIZE - PATH` 行，按状态码着色，列出跳转目标
- **配置档**：保存/加载/列出，JSON 存于 `profiles/`
- **CLI 透传**：`dirsearch-cli -u http://target/ ...` 原样驱动 dirsearch；加 `--json` 输出结构化结果

## 安装

```bash
# 从 PyPI 安装（推荐；会自动拉取 dirsearch 本体）
pip install dirsearchx
```

或从源码安装（Windows 可直接跑 `install.bat`）：

```bash
git clone --depth 1 https://github.com/maurosoria/dirsearch.git vendor/dirsearch
pip install .
```

dirsearch 自动发现顺序：`环境变量 DIRSEARCH_HOME/DIRSEARCH_PATH` → pip 安装的 `dirsearch` 包 → 包内 `vendor/dirsearch` → 常见路径 → 系统 `which dirsearch`。

## 启动

```bash
dirsearch-gui                          # 桌面 GUI
dirsearch-cli -u http://example.com    # 透传（等价裸跑 dirsearch）
dirsearch-cli --json -u http://example.com -t 30   # 结果输出为 JSON
dirsearch-cli --list-vendor            # 查看定位到的 dirsearch 根目录与版本
```

不装脚本时也可直接：

```bash
python -m dirsearchx.gui
python -m dirsearchx.cli -u http://example.com
```

## 目录结构

```
dirsearch-GUI/
├── dirsearchx/
│   ├── core/        vendor 发现 / 选项编目 / argv 构建 / 子进程 runner / 输出解析 / 预设 / 配置档
│   ├── gui/         tkinter 主屏
│   └── cli/         命令行透传
├── vendor/dirsearch/   未修改的 dirsearch（git clone）
├── pyproject.toml
├── install.bat
└── README.md
```

## 安全提醒

dirsearch 是主动探测工具，**请仅对已获授权的目标使用**。
“限速礼貌扫”预设适合对不确定的生产目标做低影响试探；正式授权测试请用全量预设。
