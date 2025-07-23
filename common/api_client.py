"""API客户端模块"""
import time
import requests
import streamlit as st
from .config import API_KEY, API_URL, API_TIMEOUT, MAX_RETRIES


def call_kimi_api(prompt, system_prompt, temperature=0.7, max_tokens=2048, max_retries=MAX_RETRIES):
    """
    调用AI API生成对话，带重试机制
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大token数
        max_retries: 最大重试次数
    
    Returns:
        str: API返回的内容或错误信息
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 5
                print(f"API速率限制，等待{wait_time}秒后重试...")
                if 'st' in globals():
                    st.warning(f"⏱️ API速率限制，等待{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return "API调用超时，请稍后重试"
            time.sleep(2)
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                return f"网络错误: {str(e)}"
            time.sleep(2)
            continue
    
    return "API调用失败：超过最大重试次数"