# QR Code Generator
这是一个基于 Flask 的二维码批量生成器应用程序。它允许用户通过 Web 界面添加、编辑、查看和删除二维码信息，并支持将所有二维码打包导出。

## 灵感来源
市面上都是都是针对单独的链接生成的二维码，但是在实际应用中，我们 often 会需要将多个链接打包成一个二维码，这样可以减少二维码的数量，提高扫描效率。

我的工作上需要生成多个二维码，但是每次都需要手动生成，比较麻烦，所以我就开发了这个应用程序。

考虑到第三方系统以及有二维码需要的信息，这个程序可以通过调用json接口，将需要的信息上传到程序中，程序会自动批量生成二维码。

## 功能特性

- 添加新的二维码信息（标题、内容、URL）
- 编辑现有二维码信息
- 查看所有二维码列表
- 删除不需要的二维码
- 一键生成所有二维码图片
- 导出所有二维码为 ZIP 文件
- 支持自定义 Logo 嵌入到二维码中
- 自动生成带标题和内容的二维码图片

## 安装依赖

在运行应用程序之前，需要安装所需的 Python 包。可以通过以下命令安装：

```bash
pip install -r requirements.txt
```

如果项目中没有 `requirements.txt` 文件，可以手动安装所需的包：

```bash
pip install Flask Pillow qrcode
```

## 运行方式

1. 确保已安装所有依赖项
2. 在项目根目录下运行以下命令启动 Flask 应用：

```bash
python app.py
```

3. 应用将在 `http://localhost:5001` 上运行

## 项目结构

```
project/
├── app.py              # Flask 应用主文件
├── wm.py               # 二维码生成模块
├── requirements.txt    # 依赖包列表
├── qr_info.db          # SQLite 数据库文件
├── logo.png            # 默认 Logo 图片
├── qr_imgs/            # 生成的二维码图片存储目录
└── templates/          # HTML 模板目录
    ├── add.html        # 添加二维码页面
    ├── edit.html       # 编辑二维码页面
    └── index.html      # 主页面
```

## API 接口

- `GET /` - 显示所有二维码列表
- `GET /add` - 显示添加二维码页面
- `POST /add` - 处理添加二维码请求
- `GET /edit/<id>` - 显示编辑二维码页面
- `POST /edit/<id>` - 处理编辑二维码请求
- `POST /delete/<id>` - 删除指定二维码
- `GET /qr_imgs/<filename>` - 显示二维码图片
- `GET /export_all` - 导出所有二维码为 ZIP 文件
- `POST /generate_all` - 一键重新生成所有二维码
- `POST /generate_qr_package` - 批量生成二维码包

## 数据库结构

使用 SQLite 数据库存储二维码信息，表结构如下：

```
CREATE TABLE qr_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT NOT NULL,
    img_url TEXT NOT NULL
);
```

## 二维码生成

二维码生成使用 `qrcode` 库，并通过 `wm.py` 中的 `create_qr_with_title` 函数实现以下特性：

- 自动换行标题和内容文本
- 支持嵌入自定义 Logo
- 设置合适的字体大小和边距
- 生成带圆角边框的美观二维码

## 效果展示

![效果展示1](pic0.jpg)
![效果展示3](pic2.png)
