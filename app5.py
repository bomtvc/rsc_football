import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from matplotlib.figure import Figure
import base64
import os
import csv
import string
import shutil

# Thiết lập trang
st.set_page_config(page_title="Bốc Thăm Bảng Đấu / Draw Tournament Groups", layout="wide")

# Danh sách 23 đội thi đấu
all_teams = [
    "HSSE-HR", "ME", "QC 1", "RC - WOOD", "PACKING 1", "WH - MAINT", "PACKING 2", "FINISHING P1",
    "QC 2", "UPH 1", "UPH 2", "PROTOTYPE", "PANEL", "MACHINING P1", "INLAY", "ASSEMBLY P1",
    "ASSEMBLY P2", "MAC-PANEL P2", "WASHING - FITTING P2", "CARTLINE P2", "METAL WORK", "TECHNICAL FINISHING", "OFFLINE P2"
]

# Tệp lưu thông tin đăng nhập
USER_FILE = "users.csv"
# Tệp lưu kết quả bốc thăm
RESULTS_FILE = "results.csv"

# Song ngữ Việt-Anh
translations = {
    "app_title": {
        "vi": "🏆 BỐC THĂM BẢNG THI ĐẤU GIẢI BÓNG ĐÁ TRUYỀN THỐNG ROCHDALE SPEARS 🏆",
        "en": "🏆 OFFICIAL GROUP STAGE DRAW – ROCHDALE SPEARS TRADITIONAL FOOTBALL TOURNAMENT 2025 🏆"
    },
    "results_tab": {
        "vi": "Kết quả bốc thăm",
        "en": "Draw Results"
    },
    "login_tab": {
        "vi": "Đăng nhập / Bốc thăm",
        "en": "Login / Draw"
    },
    "draw_header": {
        "vi": "Bốc thăm bảng thi đấu",
        "en": "Tournament Group Draw"
    },
    "remaining_teams": {
        "vi": "Còn lại",
        "en": "Remaining"
    },
    "teams": {
        "vi": "đội",
        "en": "teams"
    },
    "drawn_teams": {
        "vi": "Đã bốc thăm",
        "en": "Drawn"
    },
    "select_team": {
        "vi": "Chọn đội để bốc thăm:",
        "en": "Select team to draw:"
    },
    "all_teams_drawn": {
        "vi": "Đã bốc thăm xong tất cả các đội!",
        "en": "All teams have been drawn!"
    },
    "team_already_drawn": {
        "vi": "Đội {} đã bốc thăm rồi!",
        "en": "Team {} has already been drawn!"
    },
    "will_draw_for": {
        "vi": "Bạn sẽ bốc thăm cho đội:",
        "en": "You will draw for team:"
    },
    "team_not_found": {
        "vi": "Không tìm thấy thông tin đội của bạn!",
        "en": "Your team information was not found!"
    },
    "draw_button": {
        "vi": "Bốc thăm",
        "en": "Draw"
    },
    "reset_button": {
        "vi": "Bắt đầu lại",
        "en": "Reset"
    },
    "login_header": {
        "vi": "Đăng nhập để bốc thăm",
        "en": "Login to draw"
    },
    "username_label": {
        "vi": "Tên đội/Username",
        "en": "Team name/Username"
    },
    "password_label": {
        "vi": "Mật khẩu",
        "en": "Password"
    },
    "login_button": {
        "vi": "Đăng nhập",
        "en": "Login"
    },
    "login_error": {
        "vi": "Tên đăng nhập hoặc mật khẩu không đúng!",
        "en": "Incorrect username or password!"
    },
    "logged_in_as": {
        "vi": "Đăng nhập với tên:",
        "en": "Logged in as:"
    },
    "logout_button": {
        "vi": "Đăng xuất",
        "en": "Logout"
    },
    "spinning": {
        "vi": "Đang quay vòng quay...",
        "en": "Spinning the wheel..."
    },
    "result": {
        "vi": "Kết quả:",
        "en": "Result:"
    },
    "results_header": {
        "vi": "Kết quả bốc thăm",
        "en": "Draw Results"
    },
    "position": {
        "vi": "Vị trí",
        "en": "Position"
    },
    "group": {
        "vi": "Bảng",
        "en": "Group"
    },
    "reset_confirm": {
        "vi": "Bạn có chắc chắn muốn bắt đầu lại? Tất cả kết quả bốc thăm sẽ bị xóa!",
        "en": "Are you sure you want to reset? All draw results will be deleted!"
    },
    "reset_success": {
        "vi": "Đã reset thành công! Tất cả kết quả bốc thăm đã được xóa.",
        "en": "Reset successful! All draw results have been deleted."
    },
    "language": {
        "vi": "Ngôn ngữ:",
        "en": "Language:"
    }
}

# Hàm lấy văn bản theo ngôn ngữ
def get_text(key, lang="vi"):
    return translations.get(key, {}).get(lang, key)

# Hàm tạo mật khẩu ngẫu nhiên
def generate_password(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Hàm tạo file users.csv nếu chưa tồn tại
def create_users_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password'])
            
            # Tạo người dùng cho mỗi đội với mật khẩu ngẫu nhiên
            for team in all_teams:
                password = generate_password()
                writer.writerow([team, password])
                
            # Tạo tài khoản admin
            admin_password = "admin123"
            writer.writerow(["admin", admin_password])
            
        st.success("Đã tạo file users.csv với thông tin đăng nhập cho tất cả các đội!")
        
        # Hiển thị thông tin đăng nhập
        st.write("Thông tin đăng nhập / Login information:")
        users_data = []
        with open(USER_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Bỏ qua header
            for row in reader:
                if row[0] != "admin":  # Không hiển thị thông tin admin
                    users_data.append({"Đội / Team": row[0], "Mật khẩu / Password": row[1]})
        
        st.table(pd.DataFrame(users_data))

# Hàm tạo file results.csv nếu chưa tồn tại
def create_results_file():
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['team', 'position'])

# Hàm kiểm tra đăng nhập
def check_login(username, password):
    if not os.path.exists(USER_FILE):
        create_users_file()
        
    with open(USER_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Bỏ qua header
        for row in reader:
            if row[0] == username and row[1] == password:
                return True
    return False

# Hàm lấy danh sách đội đã bốc thăm
def get_drawn_teams():
    if not os.path.exists(RESULTS_FILE):
        create_results_file()
        return []
        
    drawn_teams = []
    with open(RESULTS_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Bỏ qua header
        for row in reader:
            drawn_teams.append(row[0])
    return drawn_teams

# Hàm lưu kết quả bốc thăm
def save_result(team, position):
    with open(RESULTS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([team, position])

# Hàm lấy kết quả bốc thăm từ file
def get_results():
    if not os.path.exists(RESULTS_FILE):
        create_results_file()
        return {}
        
    results = {}
    with open(RESULTS_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Bỏ qua header
        for row in reader:
            if len(row) >= 2:
                results[row[0]] = row[1]
    return results

# Hàm reset kết quả bốc thăm (chỉ admin)
def reset_results():
    # Tạo file results.csv mới
    with open(RESULTS_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['team', 'position'])
    
    # Cập nhật lại vị trí có sẵn
    positions = []
    for group in ['A', 'B', 'C']:
        for i in range(1, 7):
            positions.append(f"{group}{i}")
    for i in range(1, 6):
        positions.append(f"D{i}")
    st.session_state.positions = positions
    st.session_state.available_positions = positions.copy()
    
    # Reset góc quay
    st.session_state.wheel_angle = 0

# Hàm vẽ vòng quay may mắn với góc quay
def create_wheel(positions, angle=0):
    fig = Figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    
    # Số lượng phần tử trên vòng quay
    n = len(positions)
    
    # Màu sắc cho các phần tử
    colors = plt.cm.rainbow(np.linspace(0, 1, n))
    
    # Vẽ các phần tử trên vòng quay
    theta1 = angle  # Bắt đầu từ góc quay hiện tại
    theta2 = 360 / n
    
    wedges = []
    labels_pos = []
    
    for i in range(n):
        wedge = Wedge((0, 0), 0.9, theta1, theta1 + theta2, fc=colors[i])
        ax.add_patch(wedge)
        wedges.append(wedge)
        
        # Thêm nhãn
        mid_angle = np.radians((theta1 + theta1 + theta2) / 2)
        text_x = 0.5 * np.cos(mid_angle)
        text_y = 0.5 * np.sin(mid_angle)
        ax.text(text_x, text_y, positions[i], ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Lưu vị trí của nhãn để xác định kết quả
        labels_pos.append((mid_angle, positions[i]))
        
        theta1 += theta2
    
    # Thêm vòng tròn ở giữa
    center_circle = Circle((0, 0), 0.2, fc='white')
    ax.add_patch(center_circle)
    
    # Thêm mũi tên chỉ vị trí (cố định ở vị trí trên cùng)
    ax.arrow(0, 0, 0, 1, head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    return fig, labels_pos

# Hàm xác định vị trí được chọn dựa trên góc quay
def get_selected_position(labels_pos, angle):
    # Chuyển đổi góc quay sang radian
    angle_rad = np.radians(angle)
    
    # Điều chỉnh góc để phù hợp với hệ tọa độ của matplotlib
    adjusted_angle = (angle_rad - np.pi/2) % (2*np.pi)
    
    # Tìm vị trí gần nhất với mũi tên (trên cùng)
    arrow_angle = 0  # Vì đã điều chỉnh góc
    
    # Tìm vị trí có góc gần với mũi tên nhất
    min_diff = float('inf')
    selected_position = None
    
    for pos_angle, position in labels_pos:
        # Điều chỉnh góc của vị trí
        adjusted_pos_angle = (pos_angle - np.pi/2) % (2*np.pi)
        
        # Tính khoảng cách góc
        diff = min((adjusted_pos_angle - arrow_angle) % (2*np.pi), 
                   (arrow_angle - adjusted_pos_angle) % (2*np.pi))
        
        if diff < min_diff:
            min_diff = diff
            selected_position = position
    
    return selected_position

# Hàm cập nhật bảng kết quả
def update_result_table():
    # Khởi tạo bảng kết quả trống
    result_table = {
        'A': [None] * 6,  # 6 vị trí cho bảng A
        'B': [None] * 6,  # 6 vị trí cho bảng B
        'C': [None] * 6,  # 6 vị trí cho bảng C
        'D': [None] * 5,  # 5 vị trí cho bảng D
    }
    
    # Lấy kết quả từ file
    results = get_results()
    
    # Cập nhật bảng kết quả
    for team, position in results.items():
        group = position[0]  # Lấy chữ cái đầu (A, B, C, D)
        index = int(position[1:]) - 1  # Lấy số (0-based index)
        result_table[group][index] = team
    
    return result_table

# Hàm tạo HTML để phát âm thanh
def autoplay_audio(url):
    audio_html = f"""
        <audio id="wheelAudio" autoplay loop>
            <source src="{url}" type="audio/ogg">
            Your browser does not support the audio element.
        </audio>
        <script>
            var audio = document.getElementById("wheelAudio");
            audio.volume = 0.5;  // Đặt âm lượng ở mức 50%
        </script>
    """
    return audio_html

# Hàm dừng âm thanh
def stop_audio():
    stop_html = """
        <script>
            var audio = document.getElementById("wheelAudio");
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
        </script>
    """
    return stop_html

# Hàm hiển thị bảng kết quả
def display_result_table(result_table, lang="vi"):
    st.header(get_text("results_header", lang))
    
    # Tạo HTML cho bảng
    table_html = '<table class="styled-table"><thead><tr>'
    table_html += f'<th>{get_text("position", lang)}</th><th>{get_text("group", lang)} A</th><th>{get_text("group", lang)} B</th><th>{get_text("group", lang)} C</th><th>{get_text("group", lang)} D</th>'
    table_html += '</tr></thead><tbody>'
    
    # Thêm dữ liệu vào bảng
    for i in range(6):
        table_html += '<tr>'
        table_html += f'<td class="header-cell">{i+1}</td>'
        
        # Bảng A
        cell_value = result_table['A'][i] if i < len(result_table['A']) and result_table['A'][i] is not None else ""
        cell_class = "empty-cell" if cell_value == "" else ""
        cell_content = cell_value if cell_value != "" else "_____"
        table_html += f'<td class="{cell_class}">{cell_content}</td>'
        
        # Bảng B
        cell_value = result_table['B'][i] if i < len(result_table['B']) and result_table['B'][i] is not None else ""
        cell_class = "empty-cell" if cell_value == "" else ""
        cell_content = cell_value if cell_value != "" else "_____"
        table_html += f'<td class="{cell_class}">{cell_content}</td>'
        
        # Bảng C
        cell_value = result_table['C'][i] if i < len(result_table['C']) and result_table['C'][i] is not None else ""
        cell_class = "empty-cell" if cell_value == "" else ""
        cell_content = cell_value if cell_value != "" else "_____"
        table_html += f'<td class="{cell_class}">{cell_content}</td>'
        
        # Bảng D (chỉ có 5 vị trí)
        if i < 5:
            cell_value = result_table['D'][i] if i < len(result_table['D']) and result_table['D'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
        else:
            # Vị trí không tồn tại trong bảng D
            table_html += '<td class="empty-cell" style="background-color: #e0e0e0;">---</td>'
        
        table_html += '</tr>'
    
    table_html += '</tbody></table>'
    
    # Hiển thị bảng
    st.markdown(table_html, unsafe_allow_html=True)

# CSS để tạo bảng đẹp mắt hơn
css = """
<style>
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 18px;
        font-family: sans-serif;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    .styled-table thead tr {
        background-color: #009879;
        color: white;
        text-align: center;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
        border: 1px solid #dddddd;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #009879;
    }
    .empty-cell {
        color: #999;
        font-style: italic;
    }
    .header-cell {
        font-weight: bold;
        background-color: #f0f0f0;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        background-color: #f9f9f9;
    }
    .login-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .tabs-container {
        margin-bottom: 20px;
    }
    .language-selector {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    .language-selector label {
        margin-right: 10px;
    }
</style>
"""

# Hiển thị CSS
st.markdown(css, unsafe_allow_html=True)

# Đảm bảo các file cần thiết tồn tại
create_users_file()
create_results_file()

# Khởi tạo session state
if 'positions' not in st.session_state:
    # Tạo tất cả các vị trí có thể
    positions = []
    for group in ['A', 'B', 'C']:
        for i in range(1, 7):
            positions.append(f"{group}{i}")
    for i in range(1, 6):
        positions.append(f"D{i}")
    st.session_state.positions = positions

if 'available_positions' not in st.session_state:
    # Lấy vị trí đã được bốc thăm
    results = get_results()
    used_positions = list(results.values())
    
    # Tính toán vị trí còn lại
    st.session_state.available_positions = [pos for pos in st.session_state.positions if pos not in used_positions]

if 'spinning' not in st.session_state:
    st.session_state.spinning = False

if 'wheel_angle' not in st.session_state:
    st.session_state.wheel_angle = 0

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'username' not in st.session_state:
    st.session_state.username = ""

if 'language' not in st.session_state:
    st.session_state.language = "vi"

# Chọn ngôn ngữ
with st.container():
    col1, col2 = st.columns([6, 1])
    with col2:
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
        st.write(get_text("language", st.session_state.language))
        language = st.selectbox(
            label="",
            options=["vi", "en"],
            index=0 if st.session_state.language == "vi" else 1,
            format_func=lambda x: "Tiếng Việt" if x == "vi" else "English",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()

# Placeholder cho audio
audio_placeholder = st.empty()

# Tiêu đề ứng dụng
st.title(get_text("app_title", st.session_state.language))

# Tạo tabs
tab1, tab2 = st.tabs([
    get_text("results_tab", st.session_state.language), 
    get_text("login_tab", st.session_state.language)
])

# Tab 1: Kết quả bốc thăm (hiển thị cho tất cả người dùng)
with tab1:
    # Cập nhật bảng kết quả
    result_table = update_result_table()
    
    # Hiển thị bảng kết quả
    display_result_table(result_table, st.session_state.language)
    
    # Hiển thị số đội đã bốc thăm
    drawn_teams = get_drawn_teams()
    st.info(f"{get_text('drawn_teams', st.session_state.language)}: {len(drawn_teams)}/23 {get_text('teams', st.session_state.language)}")

# Tab 2: Đăng nhập và bốc thăm
with tab2:
    # Kiểm tra đăng nhập
    if not st.session_state.logged_in:
        # Form đăng nhập
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown(f'<h2 class="login-header">{get_text("login_header", st.session_state.language)}</h2>', unsafe_allow_html=True)
            
            username = st.text_input(get_text("username_label", st.session_state.language))
            password = st.text_input(get_text("password_label", st.session_state.language), type="password")
            
            if st.button(get_text("login_button", st.session_state.language)):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(get_text("login_error", st.session_state.language))
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Đã đăng nhập, hiển thị giao diện bốc thăm
        
        # Hiển thị thông tin người dùng đang đăng nhập
        st.sidebar.success(f"{get_text('logged_in_as', st.session_state.language)} {st.session_state.username}")
        
        # Nút đăng xuất
        if st.sidebar.button(get_text("logout_button", st.session_state.language)):
            for key in ['logged_in', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # Nút reset (chỉ hiển thị cho admin)
        if st.session_state.username == "admin":
            if st.sidebar.button(get_text("reset_button", st.session_state.language)):
                reset_confirm = st.sidebar.warning(get_text("reset_confirm", st.session_state.language))
                if st.sidebar.button("Confirm Reset", key="confirm_reset"):
                    reset_results()
                    st.sidebar.success(get_text("reset_success", st.session_state.language))
                    st.rerun()
        
        # Lấy danh sách đội đã bốc thăm
        drawn_teams = get_drawn_teams()
        
        # Container: Phần bốc thăm
        with st.container():
            st.header(get_text("draw_header", st.session_state.language))
            
            # Hiển thị số đội còn lại cần bốc thăm
            st.subheader(f"{get_text('remaining_teams', st.session_state.language)}: {23 - len(drawn_teams)}/23 {get_text('teams', st.session_state.language)}")
            
            # Chia cột cho phần điều khiển
            control_col1, control_col2 = st.columns([3, 1])
            
            with control_col1:
                # Kiểm tra xem người dùng hiện tại có phải là admin không
                is_admin = (st.session_state.username == "admin")
                
                if is_admin:
                    # Admin có thể chọn bất kỳ đội nào chưa bốc thăm
                    available_teams = [team for team in all_teams if team not in drawn_teams]
                    if available_teams:
                        selected_team = st.selectbox(get_text("select_team", st.session_state.language), available_teams)
                    else:
                        st.success(get_text("all_teams_drawn", st.session_state.language))
                        selected_team = None
                else:
                    # Người dùng thông thường chỉ có thể bốc thăm cho đội của mình
                    team_name = st.session_state.username
                    
                    if team_name in drawn_teams:
                        st.warning(get_text("team_already_drawn", st.session_state.language).format(team_name))
                        selected_team = None
                    elif team_name in all_teams:
                        st.info(f"{get_text('will_draw_for', st.session_state.language)} {team_name}")
                        selected_team = team_name
                    else:
                        st.error(get_text("team_not_found", st.session_state.language))
                        selected_team = None
            
            with control_col2:
                # Nút bốc thăm
                can_draw = (selected_team is not None and 
                           (is_admin or (selected_team not in drawn_teams)))
                
                if can_draw and st.button(get_text("draw_button", st.session_state.language), use_container_width=True):
                    st.session_state.spinning = True
                    st.session_state.current_team = selected_team
                    st.rerun()

        # Container: Vòng xoay và kết quả bốc thăm
        with st.container():
            # Hiển thị vòng quay may mắn
            wheel_container = st.empty()
            result_container = st.empty()
            
            if st.session_state.spinning and st.session_state.available_positions:
                # Phát âm thanh khi quay
                audio_url = "https://vongquaymayman.co/wp-content/themes/twentytwentythree-child/assets/sound/chiecnonkydieu.ogg"
                audio_placeholder.markdown(autoplay_audio(audio_url), unsafe_allow_html=True)
                
                with st.spinner(get_text("spinning", st.session_state.language)):
                    # Hiệu ứng quay
                    progress_bar = st.progress(0)
                    
                    # Số vòng quay và thời gian quay
                    total_spins = 20  # Tổng số bước quay
                    spin_duration = 2  # Thời gian quay (giây)
                    
                    # Chọn vị trí ngẫu nhiên bằng cách xác định góc dừng
                    # Tính góc cho mỗi vị trí
                    n = len(st.session_state.available_positions)
                    segment_angle = 360 / n
                    
                    # Chọn một vị trí ngẫu nhiên
                    random_index = random.randint(0, n - 1)
                    
                    # Tính góc dừng để mũi tên chỉ vào vị trí được chọn
                    # Góc dừng = góc bắt đầu của phần tử + một nửa góc của phần tử + số vòng quay ngẫu nhiên
                    target_angle = random_index * segment_angle + segment_angle / 2
                    target_angle += random.randint(5, 10) * 360  # Thêm một số vòng quay ngẫu nhiên
                    
                    # Tạo danh sách các góc quay
                    angles = []
                    current_angle = st.session_state.wheel_angle
                    
                    # Tạo hiệu ứng quay với tốc độ giảm dần
                    for i in range(total_spins):
                        # Tính góc quay cho mỗi bước
                        progress = i / total_spins
                        
                        # Sử dụng hàm easeOutCubic để tạo hiệu ứng chậm dần
                        t = 1 - (1 - progress) ** 3
                        
                        # Góc quay hiện tại
                        current_angle = current_angle + (target_angle - current_angle) * t
                        angles.append(current_angle % 360)
                    
                    # Thực hiện quay
                    labels_pos = None
                    for i, angle in enumerate(angles):
                        # Vẽ vòng quay với góc hiện tại
                        fig, labels_pos = create_wheel(st.session_state.available_positions, angle)
                        wheel_container.pyplot(fig)
                        
                        # Cập nhật thanh tiến trình
                        progress_bar.progress(int((i + 1) / total_spins * 100))
                        
                        # Tạm dừng để tạo hiệu ứng
                        time.sleep(spin_duration / total_spins)
                    
                    # Lưu góc quay cuối cùng
                    st.session_state.wheel_angle = angles[-1] % 360
                    
                    # Xác định vị trí được chọn dựa trên góc quay cuối cùng
                    selected_position = get_selected_position(labels_pos, st.session_state.wheel_angle)
                    
                    # Lưu kết quả vào file
                    save_result(st.session_state.current_team, selected_position)
                    
                    # Cập nhật danh sách vị trí còn lại
                    st.session_state.available_positions.remove(selected_position)
                    
                    # Hiển thị kết quả
                    result_container.success(f"{get_text('result', st.session_state.language)} {st.session_state.current_team} → {selected_position}")
                    
                    # Kết thúc quay và dừng âm thanh
                    audio_placeholder.markdown(stop_audio(), unsafe_allow_html=True)
                    st.session_state.spinning = False
            else:
                # Hiển thị vòng quay tĩnh
                if st.session_state.available_positions:
                    fig, _ = create_wheel(st.session_state.available_positions, st.session_state.wheel_angle)
                    wheel_container.pyplot(fig)
