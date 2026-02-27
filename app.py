import streamlit as st
import base64
from zhipuai import ZhipuAI
from PIL import Image
import io
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, timezone
import re
import requests
import json
import os

# ================= 1. 页面配置 =================
st.set_page_config(
    page_title="赛博营养师 Pro", 
    page_icon="🥑", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    div.stButton > button {
        background: linear-gradient(45deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(46,204,113,0.3);
    }
    div[data-testid="stAlert"] { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ================= 🚀 核心修复：强制北京时间 =================
BEIJING_TZ = timezone(timedelta(hours=8))

def get_today_str():
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

# ================= 2. 核心架构：统一验证系统 =================
APP_CODE = "diet"

def get_cloud_db():
    try:
        if "GITHUB_TOKEN" in st.secrets and "GIST_ID" in st.secrets:
            token = st.secrets["GITHUB_TOKEN"]
            gist_id = st.secrets["GIST_ID"]
            url = f"https://api.github.com/gists/{gist_id}"
            headers = {"Authorization": f"token {token}"}
            resp = requests.get(url, headers=headers, params={"t": datetime.now().timestamp()})
            if resp.status_code == 200:
                return json.loads(resp.json()['files']['licenses.json']['content'])
        return None
    except Exception:
        return None

def verify_license(key):
    db = get_cloud_db()
    if db and key in db:
        card = db[key]
        app_scope = card.get('app_scope') or card.get('app')
        if app_scope not in [APP_CODE, 'ALL']:
            if not key.startswith("DIET") and not key.startswith("TRY") and not key.startswith("ALL") and not key.startswith("ADMIN"):
                return False, "⚠️ 此卡密不能用于本应用"
        if card.get('status') == 'BANNED':
            return False, "🚫 此卡已被封禁"
        return True, card.get('type_name', '高级会员')
    
    if key == "vip666": return True, "👑 管理员"
    return False, "❌ 无效卡密，请检查输入"

# ================= 3. 数据库逻辑 (融合了你的高级打点逻辑) =================
DB_NAME = 'cyber_diet_final.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS food_log
                     (user_id TEXT, date TEXT, food TEXT, cal REAL, prot REAL, carb REAL, fat REAL)''')
        conn.commit()
    except Exception as e:
        st.error(f"数据库初始化失败: {e}")
    finally:
        conn.close()

def add_food_to_db(user_id, food, cal, prot, carb, fat):
    """完美融合了指挥官的打点记录与安全Tuple写入"""
    try:
        conn = sqlite3.connect(DB_NAME, timeout=10) 
        c = conn.cursor()
        today = get_today_str() # 保证是北京时间
        
        # 使用你设计的 Tuple 组装，非常严谨
        data_tuple = (str(user_id), today, str(food), float(cal), float(prot), float(carb), float(fat))
        print(f"[DEBUG] 准备插入数据: {data_tuple}")
        
        c.execute("INSERT INTO food_log VALUES (?,?,?,?,?,?,?)", data_tuple)
        conn.commit()
        
        print(f"[DEBUG] 数据插入成功: {food}")
        return True, "写入成功"
    except Exception as e:
        print(f"[DEBUG] 数据库错误: {e}")
        return False, f"写入错误: {e}"
    finally:
        conn.close()

def get_today_summary(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        today = get_today_str()
        query = "SELECT * FROM food_log WHERE date = ? AND user_id = ?"
        df = pd.read_sql_query(query, conn, params=(today, str(user_id)))
        conn.close()
        
        if df.empty: return 0, 0, 0, 0, df
        return df['cal'].sum(), df['prot'].sum(), df['carb'].sum(), df['fat'].sum(), df
    except Exception:
        return 0, 0, 0, 0, pd.DataFrame()

def clear_today_records(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        today = get_today_str()
        print(f"[DEBUG] 清除记录 - user_id: {user_id}, today: {today}")
        
        c.execute("DELETE FROM food_log WHERE date = ? AND user_id = ?", (today, str(user_id)))
        deleted_count = c.rowcount
        print(f"[DEBUG] 删除了 {deleted_count} 条记录")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DEBUG] 清除记录错误: {e}")
        return False

init_db()

# ================= 4. AI 视觉逻辑 (🚀 V16.0 概念融合引擎) =================
def analyze_food_json(image):
    try:
        client = ZhipuAI(api_key=st.secrets["ZHIPU_API_KEY"])
        buffered = io.BytesIO()
        if image.mode != 'RGB': image = image.convert('RGB')
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 🚨 教授的终极魔法：正向引导 + 强制归纳
        prompt = """
        你是一位顶级的中国饮食文化专家和营养师。
        
        【核心任务：实体归纳】
        请观察图片，找出最核心的一道主菜。图片中同一容器内的所有食材（如主料、打底的配菜、汤汁、调料）必须被视为一个**不可分割的整体**。
        
        【菜系识别微调（非常重要）】：
        1. 看到汤里有正方形或不规则的白色小块面食，且配有牛羊肉，请优先识别为陕西特色【羊肉泡馍】或【牛肉泡馍】，而不是米粉。
        2. 看到烤鱼或炖菜下面垫着的豆芽、白菜等，这是【打底配菜】，整体名称应叫【香辣烤鱼(含配菜)】或【水煮肉片(含配菜)】。
        
        【输出格式限制】：
        你必须且只能输出包含 1 个字典的 JSON 数组（除非图里明显有几盘完全隔离的菜，否则坚决只输出 1 个元素）。
        格式如下：
        [
            {
                "name": "这里填归纳后的菜名大全（如：烤鱼含底菜）",
                "cal": 估算总热量,
                "prot": 总蛋白质,
                "carb": 总碳水,
                "fat": 总脂肪,
                "desc": "点评一下这道菜，包括它的配菜热量陷阱。"
            }
        ]
        """
        response = client.chat.completions.create(
            model="glm-4v",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_base64}}]}],
            temperature=0.01, # 保持绝对冷静
        )
        
        raw_text = response.choices[0].message.content.strip()
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        
        if json_match:
            clean_json_str = json_match.group(0)
            try:
                food_data = json.loads(clean_json_str)
                if isinstance(food_data, dict):
                    food_data = [food_data]
                return food_data, None
            except json.JSONDecodeError:
                return None, f"JSON解析失败:\n{clean_json_str}"
        else:
            return None, f"AI格式错误:\n{raw_text}"
            
    except Exception as e:
        return None, f"API调用失败: {e}"

# ================= 5. 侧边栏：收银台与档案 =================
with st.sidebar:
    st.markdown("## 🥑 赛博营养师")
    
    if "is_auth" not in st.session_state: st.session_state.is_auth = False
    if "user_id" not in st.session_state: st.session_state.user_id = "default"

    if not st.session_state.is_auth:
        st.info("🔒 系统已加密，请获取卡密解锁")
        st.table(pd.DataFrame({"套餐": ["7天体验", "30天减脂", "终身VIP"], "价格": ["¥9.9", "¥29.9", "¥199"]}))
        
        st.markdown("#### 📲 扫码购卡")
        pay_tab1, pay_tab2 = st.tabs(["🟢 微信", "🔵 支付宝"])
        with pay_tab1:
            if os.path.exists("pay_wechat.png"): st.image("pay_wechat.png")
            elif os.path.exists("pay_wechat.jpg"): st.image("pay_wechat.jpg")
            else: st.warning("⚠️ 请上传 pay_wechat.png")
        with pay_tab2:
            if os.path.exists("pay_alipay.png"): st.image("pay_alipay.png")
            elif os.path.exists("pay_alipay.jpg"): st.image("pay_alipay.jpg")
            else: st.warning("⚠️ 请上传 pay_alipay.png")
        
        st.markdown("---")
        license_key = st.text_input("🔑 输入卡密", type="password", placeholder="DIET-xxxx 或 ALL-xxxx")
        st.markdown("(客服微信: liao13689209126)") 

        if st.button("🚀 联网激活"):
            with st.spinner("验证中..."):
                success, info = verify_license(license_key)
                if success:
                    st.session_state.is_auth = True
                    st.session_state.vip_info = info
                    st.session_state.user_id = license_key.strip() 
                    st.balloons()
                    st.rerun()
                else:
                    st.error(info)
                
    else:
        st.success(f"💎 {st.session_state.vip_info}")
        st.markdown(f"**通行证 ID:** `***{st.session_state.user_id[-4:]}`")
        
        st.markdown("### 🧬 身体数据")
        gender = st.radio("性别", ["男", "女"], horizontal=True)
        height = st.slider("身高(cm)", 140, 210, 175)
        weight = st.slider("体重(kg)", 40, 150, 70)
        age = st.slider("年龄", 18, 80, 30)
        act = st.selectbox("运动量", ["久坐", "轻度", "中度", "重度"])
        
        if gender == "男": bmr = 10*weight + 6.25*height - 5*age + 5
        else: bmr = 10*weight + 6.25*height - 5*age - 161
        act_map = {"久坐":1.2, "轻度":1.375, "中度":1.55, "重度":1.725}
        tdee = int(bmr * act_map[act])
        st.session_state.tdee = tdee
        st.metric("🎯 每日目标", f"{tdee} Kcal")
        
        st.markdown("---")
        if st.button("🔒 退出登录"):
            st.session_state.is_auth = False
            st.session_state.user_id = "default"
            st.rerun()

# ================= 6. 主界面逻辑 (融合了你调试信息的完美UI) =================
if not st.session_state.is_auth:
    st.markdown("# 🥑 你的 AI 减脂教练")
    st.info("👈 **请点击左上角 `>` 箭头展开侧边栏，进行支付与激活。**")
    st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=2053", use_container_width=True)
    st.markdown("### 别在最该自律的年纪，败给卡路里")

else:
    st.title("Cyber Nutritionist Pro")
    current_uid = st.session_state.user_id 
    
    # 强制获取最新数据
    t_cal, t_prot, t_carb, t_fat, t_df = get_today_summary(current_uid)
    rem_cal = st.session_state.tdee - t_cal
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 剩余", f"{int(rem_cal)}")
    col2.metric("🥩 蛋白", f"{int(t_prot)}g")
    col3.metric("🍚 碳水", f"{int(t_carb)}g")
    col4.metric("🥑 脂肪", f"{int(t_fat)}g")
    
    prog = min(t_cal / st.session_state.tdee, 1.0)
    st.progress(prog, text=f"今日已摄入 {int(t_cal)} / {st.session_state.tdee} Kcal")
    
    if not t_df.empty:
        st.markdown("#### 📊 今日摄入明细")
        st.dataframe(
            t_df[['food', 'cal', 'prot', 'carb', 'fat']].style.format({
                'cal': '{:.0f}',
                'prot': '{:.0f}',
                'carb': '{:.0f}',
                'fat': '{:.0f}'
            }),
            column_config={
                'food': '食物名称',
                'cal': '热量',
                'prot': '蛋白',
                'carb': '碳水',
                'fat': '脂肪'
            },
            hide_index=True,
            use_container_width=True
        )
    
    if st.button("🗑️ 清除今日记录", key="clear_today_main"):
        clear_today_records(current_uid)
        st.toast("✅ 今日记录已清除")
        st.rerun()
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📸 AI 视觉识别", "✍️ 手动录入", "📋 今日流水"])
    
    with tab1:
        st.info("💡 拍摄你的美食，AI 自动分析成分。")
        img_file = st.file_uploader("选择图片", type=['jpg','png','jpeg'])
        cam_file = st.camera_input("直接拍摄")
        target = img_file if img_file else cam_file
        
        if 'last_items' not in st.session_state:
            st.session_state.last_items = None
            
        if target:
            img = Image.open(target)
            st.image(img, width=300)
            
            if st.button("⚡ 开始精准识别", type="primary"):
                st.info("🔍 调试信息: 开始识别流程...")
                
                try:
                    st.info("🔍 调试信息: 图片已加载，准备调用API...")
                    
                    with st.spinner("AI 正在运用 JSON 引擎解析结构..."):
                        food_list, error_msg = analyze_food_json(img)
                        
                        st.info(f"🔍 调试信息: API调用完成")
                        st.info(f"🔍 调试信息: food_list = {food_list}")
                        st.info(f"🔍 调试信息: error_msg = {error_msg}")
                        
                        if food_list:
                            st.session_state.last_items = food_list
                            st.success(f"✅ 成功解析 {len(food_list)} 项餐品！")
                            st.rerun() 
                        else:
                            st.error(f"❌ 解析失败。原因: {error_msg}")
                except Exception as e:
                    st.error(f"❌ 识别过程发生异常: {e}")
                    import traceback
                    st.error(f"详细错误: {traceback.format_exc()}")
        
        if st.session_state.get('last_items'):
            st.markdown("#### 🍴 确认识别结果")
            
            for i, item in enumerate(st.session_state.last_items):
                st.markdown(f"**菜品 {i+1}**")
                c1, c2 = st.columns([1, 2])
                
                name = item.get('name', f'未知菜品{i}')
                cal = item.get('cal', 0)
                prot = item.get('prot', 0)
                carb = item.get('carb', 0)
                fat = item.get('fat', 0)
                
                new_name = c1.text_input("名称 (可修改)", value=name, key=f"edit_n_{i}")
                c2.caption(f"🔥 {cal} Kcal | 🥩 {prot}g | 🍚 {carb}g | 🥑 {fat}g")
                c2.info(item.get('desc', ''))
                
                st.session_state.last_items[i]['name'] = new_name
                st.divider()
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("📥 存入数据库", type="primary", use_container_width=True):
                    st.info(f"🔍 调试信息: 准备保存 {len(st.session_state.last_items)} 条记录")
                    
                    success_count = 0
                    for i, item in enumerate(st.session_state.last_items):
                        st.info(f"🔍 调试信息: 正在保存第 {i+1} 条 - {item['name']}")
                        
                        def extract_float(value):
                            if isinstance(value, (int, float)):
                                return float(value)
                            if isinstance(value, str):
                                match = re.search(r'[\d.]+', value)
                                if match:
                                    return float(match.group())
                            return 0.0
                            return 0.0
                        
                        result = add_food_to_db(
                            current_uid, 
                            item['name'], 
                            extract_float(item.get('cal',0)), 
                            extract_float(item.get('prot',0)), 
                            extract_float(item.get('carb',0)), 
                            extract_float(item.get('fat',0))
                        )
                        if result[0]:
                            success_count += 1
                        else:
                            st.error(f"❌ 第 {i+1} 条保存失败: {result[1]}")
                    
                    if success_count > 0:
                        st.info(f"🔍 调试信息: 成功保存 {success_count}/{len(st.session_state.last_items)} 条记录")
                    st.session_state.last_items = None
                    st.toast("✅ 记录成功！数据已同步。")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ 重新识别", use_container_width=True):
                    st.session_state.last_items = None
                    st.rerun()

    with tab2:
        with st.form("manual_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("食物名称 (必填)")
            c = c2.number_input("热量(Kcal) (必填)", min_value=0.0, step=10.0)
            p1, p2, p3 = st.columns(3)
            pr = p1.number_input("蛋白(g)", min_value=0.0)
            cb = p2.number_input("碳水(g)", min_value=0.0)
            ft = p3.number_input("脂肪(g)", min_value=0.0)
            
            if st.form_submit_button("➕ 添加记录"):
                if not n.strip() or c <= 0:
                    st.error("⚠️ 食物名称和热量不能为空！")
                else:
                    success, msg = add_food_to_db(current_uid, n, c, pr, cb, ft)
                    if success:
                        st.success("✅ 记录添加成功！")
                        st.rerun()
                    else:
                        st.error(msg)

    with tab3:
        if not t_df.empty:
            chart_data = pd.DataFrame({
                "类型": ["蛋白", "碳水", "脂肪"],
                "供能占比": [t_prot*4, t_carb*4, t_fat*9]
            })
            chart = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
                theta="供能占比", color="类型"
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
            
            st.dataframe(t_df[['food','cal','prot','carb','fat']], use_container_width=True)
            
            if st.button("🗑️ 清空今日记录"):
                if clear_today_records(current_uid):
                    st.success("今日记录已清空")
                    st.rerun()
                else:
                    st.error("清空失败，请重试")
        else:
            st.info("🍽️ 今天还没有进食记录，赶快去 Tab 1 拍照吧！")