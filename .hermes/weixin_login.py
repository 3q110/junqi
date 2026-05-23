#!/usr/bin/env python3
"""
微信登录脚本 - 使用 itchat-uos 扫码登录
登录成功后保存 cookie 到文件，供 Hermes Gateway 使用
"""

import itchat
import json
import os
import time
import sys

# 保存登录状态的文件
COOKIE_FILE = os.path.expanduser("~/.hermes/weixin_cookie.json")

def save_cookie(session):
    """保存 cookie 到文件"""
    cookie_dict = {}
    for cookie in session.cookies:
        cookie_dict[cookie.name] = cookie.value
    
    with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookie_dict, f, ensure_ascii=False, indent=2)
    print(f"Cookie 已保存到: {COOKIE_FILE}")

def load_cookie():
    """从文件加载 cookie"""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def on_message(msg):
    """消息处理回调"""
    print(f"\n[{msg['FromUserName']}] {msg['Text']}")
    # 简单的自动回复
    if msg['Type'] == 'Text':
        reply = f"收到你的消息: {msg['Text']}"
        itchat.send(reply, toUserName=msg['FromUserName'])
        print(f"已回复: {reply}")

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    """自动回复文本消息"""
    if msg['User']['UserName'] != 'filehelper':
        reply = f"我是 Hermes Agent，收到你的消息: {msg['Text']}"
        itchat.send(reply, toUserName=msg['User']['UserName'])
        return reply

def main():
    print("=" * 50)
    print("Hermes Agent - 微信登录")
    print("=" * 50)
    
    # 检查是否已有 cookie
    cookie = load_cookie()
    if cookie:
        print("\n发现已有的登录状态，尝试使用...")
        # 这里需要重新登录，因为 cookie 可能会过期
        pass
    
    print("\n请用微信扫描下方二维码登录...\n")
    
    # 启用 hot reload，这样登录状态会持久化
    itchat.auto_login(
        enableCmdQR=2,
        hotReload=True
    )
    
    print("\n" + "=" * 50)
    print("微信登录成功！")
    print(f"当前用户: {itchat.storage_cls.user.get('NickName', 'Unknown')}")
    print("=" * 50)
    
    # 开始接收消息
    print("\n开始接收消息... (按 Ctrl+C 退出)")
    try:
        itchat.run()
    except KeyboardInterrupt:
        print("\n已退出")

if __name__ == "__main__":
    main()
