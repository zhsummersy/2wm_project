import os
import sqlite3
import zipfile
import tempfile
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from werkzeug.utils import secure_filename
from wm import create_qr_with_title  # 导入你的二维码生成函数

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'qr_imgs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_PATH = 'qr_info.db'

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS qr_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT NOT NULL,
            img_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, content, url, img_url FROM qr_info ORDER BY id DESC')
    qr_list = c.fetchall()
    conn.close()
    return render_template('index.html', qr_list=qr_list)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Sanitize form data to prevent newline characters in headers
        title = request.form['title'].strip().replace('\n', ' ').replace('\r', ' ')
        content = request.form['content'].strip().replace('\n', ' ').replace('\r', ' ')
        url_val = request.form['url'].strip().replace('\n', ' ').replace('\r', ' ')
        logo_file = request.files.get('logo')
        default_logo_path = os.path.join(app.root_path, 'logo.png')
        logo_path = default_logo_path  # 默认使用logo.png
        if logo_file and logo_file.filename:
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
        # 生成二维码图片
        # 使用标题和内容拼接生成文件名，但确保文件名安全
        # 对于中文文件名，我们保留原始字符但添加基本安全处理
        combined_name = f"{title}_{content}"
        safe_name = combined_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        img_filename = f"{safe_name}.png"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        create_qr_with_title(
            url_val, title, img_path,
            font_size=30, padding=15, top_text=content,
            logo_path=logo_path, logo_scale=0.18
        )
        # 存入数据库
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO qr_info (title, content, url, img_url) VALUES (?, ?, ?, ?)',
                  (title, content, url_val, img_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    default_logo = 'logo.png'  # 传递默认logo给模板
    return render_template('add.html', default_logo=default_logo)

@app.route('/edit/<int:qr_id>', methods=['GET', 'POST'])
def edit(qr_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT title, content, url, img_url FROM qr_info WHERE id=?', (qr_id,))
    qr = c.fetchone()
    if not qr:
        conn.close()
        return "二维码不存在", 404
    if request.method == 'POST':
        # Sanitize form data to prevent newline characters in headers
        title = request.form['title'].strip().replace('\n', ' ').replace('\r', ' ')
        content = request.form['content'].strip().replace('\n', ' ').replace('\r', ' ')
        url_val = request.form['url'].strip().replace('\n', ' ').replace('\r', ' ')
        logo_file = request.files.get('logo')
        default_logo_path = os.path.join(app.root_path, 'logo.png')
        logo_path = default_logo_path  # 默认使用logo.png
        if logo_file and logo_file.filename:
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
        # 重新生成二维码图片
        # 使用标题和内容拼接生成文件名，但确保文件名安全
        # 对于中文文件名，我们保留原始字符但添加基本安全处理
        combined_name = f"{title}_{content}"
        safe_name = combined_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        img_filename = f"{safe_name}.png"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        create_qr_with_title(
            url_val, title, img_path,
            font_size=30, padding=15, top_text=content,
            logo_path=logo_path, logo_scale=0.18
        )
        # 更新数据库
        c.execute('UPDATE qr_info SET title=?, content=?, url=?, img_url=? WHERE id=?',
                  (title, content, url_val, img_filename, qr_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    default_logo = 'logo.png'  # 传递默认logo给模板
    return render_template('edit.html', qr_id=qr_id, title=qr[0], content=qr[1], url=qr[2], img_url=qr[3], default_logo=default_logo)

@app.route('/qr_imgs/<filename>')
def qr_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/export_all')
def export_all():
    # 连接数据库获取所有二维码信息
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT title, img_url FROM qr_info')
    qr_codes = c.fetchall()
    conn.close()
    
    # 创建临时ZIP文件
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    # 将所有二维码图片添加到ZIP文件
    with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
        for title, img_url in qr_codes:
            # Sanitize title to prevent newline characters in headers
            sanitized_title = title.strip().replace('\n', ' ').replace('\r', ' ')
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_url)
            if os.path.exists(img_path):
                # 将文件添加到ZIP中
                zipf.write(img_path, img_url)
    
    # 发送ZIP文件供下载
    return send_file(temp_zip.name, as_attachment=True, download_name='qr_codes.zip')

@app.route('/generate_all', methods=['POST'])
def generate_all():
    # 连接数据库获取所有二维码信息
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, content, url FROM qr_info')
    qr_codes = c.fetchall()
    conn.close()
    
    default_logo_path = os.path.join(app.root_path, 'logo.png')
    
    # 重新生成所有二维码
    for id, title, content, url in qr_codes:
        # 生成安全的文件名
        combined_name = f"{title}_{content}"
        safe_name = combined_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        img_filename = f"{safe_name}.png"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        
        # 生成二维码图片
        create_qr_with_title(
            url, title, img_path,
            font_size=30, padding=15, top_text=content,
            logo_path=default_logo_path, logo_scale=0.18
        )
        
        # 更新数据库中的img_url
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE qr_info SET img_url=? WHERE id=?', (img_filename, id))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:qr_id>', methods=['POST'])
def delete(qr_id):
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 获取二维码信息
    c.execute('SELECT img_url FROM qr_info WHERE id=?', (qr_id,))
    qr = c.fetchone()
    
    if qr:
        img_filename = qr[0]
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        
        # 从数据库删除记录
        c.execute('DELETE FROM qr_info WHERE id=?', (qr_id,))
        conn.commit()
        
        # 删除二维码图片文件
        if os.path.exists(img_path):
            os.remove(img_path)
    
    conn.close()
    return redirect(url_for('index'))

@app.route('/generate_qr_package', methods=['POST'])
def generate_qr_package():
    # 获取JSON数据
    data = request.get_json()
    qr_list = data.get('qr_list', [])
    
    # 创建临时ZIP文件
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    default_logo_path = os.path.join(app.root_path, 'logo.png')
    
    # 生成二维码并添加到ZIP文件
    with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
        for item in qr_list:
            # Sanitize data to prevent newline characters in headers
            title = item.get('title', '').strip().replace('\n', ' ').replace('\r', ' ')
            content = item.get('content', '').strip().replace('\n', ' ').replace('\r', ' ')
            url = item.get('url', '').strip().replace('\n', ' ').replace('\r', ' ')
            
            # 生成安全的文件名
            combined_name = f"{title}_{content}"
            safe_name = combined_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            img_filename = f"{safe_name}.png"
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            
            # 生成二维码图片
            create_qr_with_title(
                url, title, img_path,
                font_size=30, padding=15, top_text=content,
                logo_path=default_logo_path, logo_scale=0.18
            )
            
            # 将文件添加到ZIP中
            if os.path.exists(img_path):
                zipf.write(img_path, img_filename)
    
    # 发送ZIP文件供下载
    return send_file(temp_zip.name, as_attachment=True, download_name='qr_package.zip')

if __name__ == '__main__':
    app.run(debug=True, port=5001)