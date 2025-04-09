import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from matplotlib.figure import Figure
import base64

# Thiết lập trang
st.set_page_config(page_title="Official Group Stage Draw", layout="wide")

# Tiêu đề ứng dụng
st.title("🏆 BỐC THĂM BẢNG THI ĐẤU GIẢI BÓNG ĐÁ TRUYỀN THỐNG ROCHDALE SPEARS 🏆\n Official Group Stage Draw – Rochdale Spears Traditional Football Tournament 2025")

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
    st.session_state.available_positions = st.session_state.positions.copy()

if 'results' not in st.session_state:
    st.session_state.results = {}

if 'spinning' not in st.session_state:
    st.session_state.spinning = False

if 'wheel_angle' not in st.session_state:
    st.session_state.wheel_angle = 0

if 'result_table' not in st.session_state:
    # Khởi tạo bảng kết quả trống
    st.session_state.result_table = {
        'A': [None] * 6,  # 6 vị trí cho bảng A
        'B': [None] * 6,  # 6 vị trí cho bảng B
        'C': [None] * 6,  # 6 vị trí cho bảng C
        'D': [None] * 5,  # 5 vị trí cho bảng D
    }

# Danh sách 23 đội thi đấu (bạn có thể thay đổi tên các đội)
all_teams = [
    "HSSE-HR", "ME", "QC 1", "RC - WOOD", "PACKING 1", "WH - MAINT", "PACKING 2", "FINISHING P1",
    "QC 2", "UPH 1", "UPH 2", "PROTOTYPE", "PANEL", "MACHINING P1", "INLAY", "ASSEMBLY P1",
    "ASSEMBLY P2", "MAC-PANEL P2", "WASHING - FITTING P2", "CARTLINE P2", "METAL WORK", "TECHNICAL FINISHING ", "OFFLINE P2"
]

# Lọc các đội đã được bốc thăm
if 'used_teams' not in st.session_state:
    st.session_state.used_teams = []

available_teams = [team for team in all_teams if team not in st.session_state.used_teams]

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
    # Trong matplotlib, 0 độ là bên phải, 90 độ là trên cùng
    # Chúng ta cần điều chỉnh để 0 độ là trên cùng
    adjusted_angle = (angle_rad - np.pi/2) % (2*np.pi)
    
    # Tìm vị trí gần nhất với mũi tên (trên cùng)
    # Mũi tên ở vị trí 90 độ (π/2 radian)
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
def update_result_table(position, team):
    group = position[0]  # Lấy chữ cái đầu (A, B, C, D)
    index = int(position[1:]) - 1  # Lấy số (0-based index)
    st.session_state.result_table[group][index] = team

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
</style>
"""

# Hiển thị CSS
st.markdown(css, unsafe_allow_html=True)

# Placeholder cho audio
audio_placeholder = st.empty()

# Container 1: Phần droplist và button (trên)
with st.container():
    st.header("Bốc thăm bảng thi đấu")
    
    # Hiển thị số đội còn lại cần bốc thăm
    st.subheader(f"Còn lại: {len(available_teams)}/23 đội")
    
    # Chia cột cho phần điều khiển
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    
    with control_col1:
        if available_teams:
            # Dropdown để chọn đội
            selected_team = st.selectbox("Chọn đội để bốc thăm:", available_teams)
        else:
            st.success("Đã bốc thăm xong tất cả các đội!")
            selected_team = None
    
    with control_col2:
        # Nút bốc thăm
        if available_teams and st.button("Bốc thăm", use_container_width=True):
            st.session_state.spinning = True
            st.session_state.current_team = selected_team
            st.session_state.used_teams.append(selected_team)
            st.rerun()
            
    with control_col3:
        # Nút reset
        if st.button("Bắt đầu lại", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Container 2: Vòng xoay và kết quả bốc thăm (dưới)
with st.container():
    # Chia cột cho vòng xoay và kết quả
    wheel_col, results_col = st.columns([2, 5])
    
    # Cột 1: Vòng xoay
    with wheel_col:
        # Hiển thị vòng quay may mắn
        wheel_container = st.empty()
        result_container = st.empty()
        
        if st.session_state.spinning and st.session_state.available_positions:
            # Phát âm thanh khi quay
            audio_url = "https://vongquaymayman.co/wp-content/themes/twentytwentythree-child/assets/sound/chiecnonkydieu.ogg"
            audio_placeholder.markdown(autoplay_audio(audio_url), unsafe_allow_html=True)
            
            with st.spinner("Đang quay vòng quay..."):
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
                
                # Lưu kết quả
                st.session_state.results[st.session_state.current_team] = selected_position
                st.session_state.available_positions.remove(selected_position)
                
                # Cập nhật bảng kết quả
                update_result_table(selected_position, st.session_state.current_team)
                
                # Hiển thị kết quả
                result_container.success(f"Kết quả: {st.session_state.current_team} → {selected_position}")
                
                # Kết thúc quay và dừng âm thanh
                audio_placeholder.markdown(stop_audio(), unsafe_allow_html=True)
                st.session_state.spinning = False
        else:
            # Hiển thị vòng quay tĩnh
            if st.session_state.available_positions:
                fig, _ = create_wheel(st.session_state.available_positions, st.session_state.wheel_angle)
                wheel_container.pyplot(fig)
    
    # Cột 2: Kết quả bốc thăm
    with results_col:
        st.header("Group Draw Results/ Kết quả bốc thăm")
        
        # Tạo DataFrame cho bảng kết quả
        result_df = pd.DataFrame({
            'Vị trí': list(range(1, 7)),
            'Bảng/Group A': [st.session_state.result_table['A'][i] if i < len(st.session_state.result_table['A']) else None for i in range(6)],
            'Bảng B': [st.session_state.result_table['B'][i] if i < len(st.session_state.result_table['B']) else None for i in range(6)],
            'Bảng C': [st.session_state.result_table['C'][i] if i < len(st.session_state.result_table['C']) else None for i in range(6)],
            'Bảng D': [st.session_state.result_table['D'][i] if i < len(st.session_state.result_table['D']) else None for i in range(5)] + [None],
        })
        
        # Tạo HTML cho bảng
        table_html = '<table class="styled-table"><thead><tr>'
        table_html += '<th>Vị trí</th><th>Bảng A</th><th>Bảng B</th><th>Bảng C</th><th>Bảng D</th>'
        table_html += '</tr></thead><tbody>'
        
        # Thêm dữ liệu vào bảng
        for i in range(6):
            table_html += '<tr>'
            table_html += f'<td class="header-cell">{i+1}</td>'
            
            # Bảng A
            cell_value = st.session_state.result_table['A'][i] if i < len(st.session_state.result_table['A']) and st.session_state.result_table['A'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
            
            # Bảng B
            cell_value = st.session_state.result_table['B'][i] if i < len(st.session_state.result_table['B']) and st.session_state.result_table['B'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
            
            # Bảng C
            cell_value = st.session_state.result_table['C'][i] if i < len(st.session_state.result_table['C']) and st.session_state.result_table['C'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
            
            # Bảng D (chỉ có 5 vị trí)
            if i < 5:
                cell_value = st.session_state.result_table['D'][i] if i < len(st.session_state.result_table['D']) and st.session_state.result_table['D'][i] is not None else ""
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
