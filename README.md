# Binance OI watcher → Telegram

轻量脚本，用于轮询 Binance 永续合约的未平仓量（Open Interest），检测异常涨跌并推送到 Telegram 机器人。

## 特性
- 支持多个交易对轮询，定制轮询频率
- 绝对值或百分比阈值触发告警，内置冷却时间避免重复刷屏
- 状态落地到 JSON 文件，重启后继续追踪
- 使用 `aiohttp` 进行异步请求，轻依赖即可运行

## 快速开始
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置环境变量（最少只需监听标的）：
   ```bash
   export SYMBOLS=BTCUSDT,ETHUSDT
   export TELEGRAM_TOKEN=your_bot_token
   export TELEGRAM_CHAT_ID=your_chat_id
   ```
   可选参数：`POLL_INTERVAL`（秒，默认 15）、`PCT_THRESHOLD`（默认 0.05 即 5%）、`ABS_THRESHOLD`（绝对 OI 变动量）、`COOLDOWN`（冷却秒数，默认 300）。
3. 运行：
   ```bash
   python -m src.main
   ```

## 目录结构
- `src/config.py`：环境变量配置解析
- `src/datasource.py`：Binance REST 数据获取（OI 与价格）
- `src/detector.py`：阈值与冷却逻辑
- `src/notifier.py`：Telegram 推送
- `src/state.py`：状态持久化（JSON）
- `src/oi_monitor.py`：监控主循环
- `src/main.py`：入口脚本

## 注意事项
- Telegram 未配置时仍可运行，但会跳过告警发送。
- 使用公开 REST 接口，无需 API Key；若网络不可达，请自行配置代理。
