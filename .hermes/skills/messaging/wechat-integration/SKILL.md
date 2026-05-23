---
name: wechat-integration
description: "Connect Hermes Agent to WeChat (微信) via itchat-uos. Covers QR code login, message handling, cookie persistence, and gateway integration."
version: 1.0.0
author: hermes-agent
license: MIT
platforms: [linux, macos, wsl]
---

# WeChat (微信) Integration

Connect Hermes Agent to WeChat using `itchat-uos` for QR code login and message relay.

## Prerequisites

- Python 3.11+
- `itchat-uos` package
- A WeChat account (must support uos protocol)

## Quick Setup

### Step 1: Install Dependencies

The `execute_code` sandbox typically has no `pip` and no `sudo`. Use `uv` to create an isolated venv:

```bash
# 1. Create a virtual environment with uv
uv venv ~/.hermes/weixin_venv

# 2. Install itchat into it
uv pip install -p ~/.hermes/weixin_venv/bin/python3 itchat-uos

# 3. Verify
~/.hermes/weixin_venv/bin/python3 -c "import itchat; print(itchat.__version__)"
```

**Pitfall:** If `uv` is not available, try `pipx install comfy-cli` or check if `pip` exists. If neither works and you lack `sudo`, you may need to use a different approach or request the user to install packages.

### Step 2: Login via QR Code

Run the login script with the venv Python:

```bash
~/.hermes/weixin_venv/bin/python3 ~/.hermes/weixin_login.py
```

The script uses `itchat.auto_login(enableCmdQR=2, hotReload=True)` which:
- Displays a QR code in the terminal (rendered as ASCII art)
- Waits for the user to scan with WeChat mobile app
- On successful scan, logs in and persists session state (hotReload)

**Pitfall:** `itchat.auto_login()` does NOT accept a `callback` parameter in `itchat-uos` — remove it if you get `TypeError: auto_login() got an unexpected keyword argument 'callback'`.

### Step 3: Use with Hermes Gateway

After login, integrate with Hermes Gateway:

```bash
hermes gateway setup
# Select "Weixin / WeChat" from the platform list
# Follow the prompts to configure
```

## Supported Platforms

Hermes Gateway supports these WeChat-related platforms:
- **Weixin / WeChat** — personal WeChat (via itchat-uos)
- **WeCom (Enterprise WeChat)** — enterprise WeChat
- **WeCom Callback (Self-Built App)** — enterprise WeChat with custom app

## Message Handling

The login script includes a basic message handler:

```python
@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    """Auto-reply to text messages"""
    if msg['User']['UserName'] != 'filehelper':
        reply = f"我是 Hermes Agent，收到你的消息: {msg['Text']}"
        itchat.send(reply, toUserName=msg['User']['UserName'])
        return reply
```

Customize this handler in `~/.hermes/weixin_login.py` to integrate with Hermes' tool access.

## File Locations

| File | Purpose |
|------|---------|
| `~/.hermes/weixin_login.py` | Login and message handling script |
| `~/.hermes/weixin_venv/` | Python virtual environment |
| `~/.hermes/weixin_cookie.json` | Persisted login cookie (if enabled) |

## Troubleshooting

### QR code not displaying
- Ensure terminal supports Unicode/block characters
- Try `enableCmdQR=1` for simpler ASCII, or `enableCmdQR=2` for block characters

### Login fails after scan
- WeChat may flag the account for security — try on a different device
- The `hotReload=True` flag persists session for 24 hours

### `ModuleNotFoundError: No module named 'itchat'`
- You're running with system Python instead of the venv Python
- Always use `~/.hermes/weixin_venv/bin/python3` to run the script

### No pip / sudo available
- Use `uv` (usually pre-installed with Hermes) as shown above
- If `uv` is also unavailable, ask the user to install packages manually

## Pitfalls

1. **`callback` parameter not supported** — `itchat-uos`'s `auto_login()` does not accept `callback=save_cookie`. Remove it.
2. **Always use venv Python** — the venv Python path is `~/.hermes/weixin_venv/bin/python3`, NOT system `python3`.
3. **No sudo in sandbox** — the `execute_code` sandbox has no `sudo` and no `pip`. Always use `uv` for package installation.
4. **WSL2 QR codes** — in WSL, the QR code renders in the terminal. Make sure your terminal emulator supports the block characters used.
5. **Session expiry** — hotReload persists for ~24 hours. After expiry, re-scan the QR code.