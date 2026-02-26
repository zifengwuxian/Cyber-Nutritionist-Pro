import streamlit as st
import requests
import json
from datetime import datetime

def check_license(input_key, current_app_code):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        gist_id = st.secrets["GIST_ID"]
        filename = "matrix_licenses.json"
        
        headers = {"Authorization": f"token {token}"}
        url = f"https://api.github.com/gists/{gist_id}?t={datetime.now().timestamp()}"
        
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return False, f"云端矩阵连接失败 ({resp.status_code})", None
            
        db = json.loads(resp.json()['files'][filename]['content'])
    except Exception as e:
        return False, f"验证系统维护中: {e}", None

    if input_key not in db:
        return False, "❌ 卡密不存在或输入有误", None
    
    card = db[input_key]
    
    if card.get('status') == 'BANNED':
        return False, "🚫 此卡密已被系统封禁", None
        
    app_scope = card.get('app_scope')
    if app_scope not in [current_app_code, 'ALL']:
        if not input_key.startswith(current_app_code.upper()) and not input_key.startswith("TRY") and not input_key.startswith("ALL"):
            return False, f"⚠️ 这是一张【{card.get('type_name')}】卡，无法解锁本项目", None

    return True, "验证通过", card.get('type_name', '尊贵会员')
