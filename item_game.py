# -*- coding: utf-8 -*-
# item_game.py - 修复编码和API调用问题
import requests
import json
import sys
import random

# DeepSeek API配置 - 从config.py导入
try:
    from config import DEEPSEEK_API_KEY
except ImportError:
    # 如果找不到config.py，使用备用模式
    DEEPSEEK_API_KEY = ""
    print("提示：请创建config.py文件并配置API密钥以使用完整AI功能", file=sys.stderr)

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def call_deepseek_api(messages):
    """调用DeepSeek API并处理编码问题"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        # 设置超时并发送请求
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 显式设置编码为UTF-8以避免乱码[citation:9]
        if response.encoding is None or response.encoding.lower() != 'utf-8':
            response.encoding = 'utf-8'
            
        return response.json()
    except Exception as e:
        print(f"API调用错误: {str(e)}", file=sys.stderr)
        return None

def generate_secret_item():
    """生成秘密物品"""
    import time
    
    categories = ["household items", "electronic devices", "animals", "tools", 
                  "clothing", "food", "vehicles", "sports equipment", "musical instruments"]
    random_category = random.choice(categories)
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a game host for a guessing game. Randomly choose a common object from {random_category} category.

Generate an object and 5 hints. Return STRICT JSON format: {{"item": "object name", "hints": ["hint1", "hint2", "hint3", "hint4", "hint5"]}}.

IMPORTANT:
- Use ONLY English
- Hints should go from vague to specific
- First hints should be very vague
- Object name must be in English"""
        },
        {
            "role": "user", 
            "content": f"Generate a random secret object from {random_category} category. Timestamp: {time.time()}"
        }
    ]
    
    result = call_deepseek_api(messages)
    if result and "choices" in result:
        content = result["choices"][0]["message"]["content"]
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            if "item" in data and "hints" in data:
                # 确保物品名是英文
                if any('\u4e00' <= char <= '\u9fff' for char in data['item']):
                    print("DEBUG: 检测到中文，使用备用物品", file=sys.stderr)
                    return get_fallback_item()
                print(f"DEBUG: Generated - {data['item']} (category: {random_category})", file=sys.stderr)
                return data
        except json.JSONDecodeError:
            print("JSON parse failed, using fallback", file=sys.stderr)
    
    return get_fallback_item()

def get_fallback_item():
    """备用物品库 - 全英文"""
    items = [
        {
            "item": "hammer",
            "hints": [
                "I have a handle",
                "I am used for hitting things",
                "I am a tool",
                "I have a heavy head",
                "I am used with nails"
            ]
        },
        {
            "item": "mobile phone", 
            "hints": [
                "I fit in pockets",
                "I make calls",
                "I have a screen",
                "People use me daily", 
                "I need charging"
            ]
        },
        {
            "item": "book",
            "hints": [
                "I have pages",
                "I contain stories", 
                "People read me",
                "I have a cover",
                "I am made of paper"
            ]
        }
    ]
    return random.choice(items)

def get_fallback_item():
    """当API失败时使用备用物品"""
    items = [
        {
            "item": "mobile phone",
            "hints": [
                "I can fit in your pocket",
                "I can make calls and send messages",
                "I have a touch screen",
                "People often stare at me",
                "I need charging to work"
            ]
        },
        {
            "item": "elephant",
            "hints": [
                "I am very large but not a building",
                "I have a long trunk",
                "I live in Africa and Asia",
                "I have good memory",
                "I am the largest land animal"
            ]
        },
        {
            "item": "book",
            "hints": [
                "I have a cover",
                "I contain knowledge and stories",
                "People read me to learn",
                "I have many pages",
                "I am usually made of paper"
            ]
        },
        {
            "item": "computer",
            "hints": [
                "I have a screen and keyboard",
                "I can run programs",
                "I can connect to the internet",
                "People use me for work and entertainment",
                "I need electricity to work"
            ]
        },
        {
            "item": "clock",
            "hints": [
                "I have hands but no fingers",
                "I show the time",
                "I can be on the wall or on your wrist",
                "I tick every second",
                "I help people be punctual"
            ]
        }
    ]
    return random.choice(items)

def check_guess(secret_item, user_guess):
    """检查用户猜测是否正确"""
    # 简单字符串匹配，避免API调用复杂性
    user_lower = user_guess.lower().strip()
    secret_lower = secret_item.lower()
    
    # 直接匹配
    if user_lower == secret_lower:
        return {"is_correct": True, "feedback": "Correct! You win!"}
    
    # 部分匹配
    if user_lower in secret_lower or secret_lower in user_lower:
        return {"is_correct": True, "feedback": "Close enough! Correct!"}
    
    # 常见同义词
    synonyms = {
        "mobile phone": ["phone", "cellphone", "smartphone", "telephone"],
        "elephant": ["elephants", "pachyderm"],
        "book": ["books", "novel", "textbook", "reading"],
        "computer": ["pc", "laptop", "desktop", "macbook"]
    }
    
    if secret_item in synonyms:
        if user_lower in synonyms[secret_item]:
            return {"is_correct": True, "feedback": "Good thinking! Correct!"}
    
    return {"is_correct": False, "feedback": "Not correct, try again"}

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "generate":
                result = generate_secret_item()
                # 使用ensure_ascii=False确保正确显示，但设置UTF-8编码
                print(json.dumps(result, ensure_ascii=False))
                
            elif sys.argv[1] == "check" and len(sys.argv) > 3:
                secret_item = sys.argv[2]
                user_guess = sys.argv[3]
                result = check_guess(secret_item, user_guess)
                print(json.dumps(result, ensure_ascii=False))
                
    except Exception as e:
        # 紧急回退
        print('{"item": "book", "hints": ["I have covers", "I contain stories", "People read me", "I have pages", "I am made of paper"]}')