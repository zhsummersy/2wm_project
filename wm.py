import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def create_qr_with_title(url, title, output_path="qrcode.png", font_size=20, padding=10, top_text="", logo_path=None, logo_scale=0.18):
    """
    生成美化的二维码，顶部和底部均可显示内容，二维码整体居中，文字内容居中对齐，可在二维码中间嵌入logo
    参数:
        url (str): 要编码的URL
        title (str): 底部标题(支持中文)
        output_path (str): 输出图片路径
        font_size (int): 字体大小
        padding (int): 标题与二维码之间的间距
        top_text (str): 显示在二维码上的内容
        logo_path (str): logo图片路径
        logo_scale (float): logo占二维码宽度比例，建议0.15~0.22
    """
    # 创建基本二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高纠错，适合嵌logo
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 获取二维码图像并转换为RGB模式
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    qr_width, qr_height = qr_img.size

    # 尝试加载字体
    try:
        font_path = "NotoSansSC-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 处理文本换行
    def wrap_text(text, max_width, font):
        if not text:
            return [""]
        lines = []
        for paragraph in text.split('\n'):
            # 对于每个段落，按字符逐个检查是否需要换行
            current_line = ""
            for char in paragraph:
                test_line = current_line + char
                bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:  # 如果当前行不为空，则换行
                        lines.append(current_line)
                        current_line = char
                    else:  # 如果单个字符就超出宽度，则强制添加
                        lines.append(test_line)
                        current_line = ""
            if current_line:  # 添加最后一行
                lines.append(current_line)
        return lines
    
    # 计算多行文本尺寸
    def get_multiline_text_size(lines, font):
        if not lines:
            return 0, 0
        max_width = 0
        total_height = 0
        draw_tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        for line in lines:
            bbox = draw_tmp.textbbox((0, 0), line, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            max_width = max(max_width, width)
            total_height += height
        return max_width, total_height

    # 处理顶部和底部文本
    max_text_width = qr_width - padding * 2  # 最大文本宽度
    top_lines = wrap_text(top_text, max_text_width, font)
    title_lines = wrap_text(title, max_text_width, font)
    
    # 计算顶部和底部文字尺寸
    top_width, top_height = get_multiline_text_size(top_lines, font)
    title_width, title_height = get_multiline_text_size(title_lines, font)

    # 增加顶部文字与二维码的距离
    top_margin = padding * 2 + top_height

    # 新图像尺寸：顶部+二维码+底部+留白
    extra_bottom = int(title_height * 0.3)
    extra_top = int(top_height * 0.3)
    # 保证新图像宽度为正方形（二维码宽度+两侧最大文字宽度+边距）
    min_side = max(qr_width, top_width + padding * 2, title_width + padding * 2)
    new_width = min_side + padding * 2
    new_height = top_height + qr_height + title_height + padding * 4 + extra_top + extra_bottom + padding
    # 如果高度比宽度大，则补齐为正方形
    final_side = max(new_width, new_height)
    new_img = Image.new('RGB', (final_side, final_side), 'white')

    # 计算二维码粘贴位置（居中）
    qr_x = (final_side - qr_width) // 2
    qr_y = top_height + top_margin + extra_top

    new_img.paste(qr_img, (qr_x, qr_y))

    draw = ImageDraw.Draw(new_img)

    # 绘制顶部文字（居中对齐）
    top_start_y = padding
    line_spacing = 1.2  # 行间距系数
    for i, line in enumerate(top_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        text_x = (final_side - line_width) // 2  # 文字居中
        top_y = top_start_y + int(i * line_height * line_spacing)
        draw.text((text_x, top_y), line, font=font, fill="black")

    # 绘制底部文字（居中对齐）
    title_start_y = qr_y + qr_height + padding
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        text_x = (final_side - line_width) // 2  # 文字居中
        title_y = title_start_y + int(i * line_height * line_spacing)
        draw.text((text_x, title_y), line, font=font, fill="black")

    # 美化二维码边框（只画在二维码四周，不穿过文字）
    border_color = (100, 149, 237)  # 淡蓝色
    border_width = 4
    rect_x0 = qr_x - border_width
    rect_y0 = qr_y - border_width
    rect_x1 = qr_x + qr_width + border_width
    rect_y1 = qr_y + qr_height + border_width
    draw.rounded_rectangle(
        [rect_x0, rect_y0, rect_x1, rect_y1],
        radius=16, outline=border_color, width=border_width
    )

    # 在二维码中心嵌入logo
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_size = int(qr_width * logo_scale)
        logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
        # 白色圆角背景
        bg_size = int(logo_size * 1.25)
        bg = Image.new("RGBA", (bg_size, bg_size), (255, 255, 255, 255))
        bg_draw = ImageDraw.Draw(bg)
        bg_draw.rounded_rectangle([0, 0, bg_size, bg_size], radius=bg_size//4, fill=(255,255,255,255))
        bg.paste(logo_img, ((bg_size - logo_size)//2, (bg_size - logo_size)//2), logo_img)
        # 居中粘贴
        logo_x = qr_x + (qr_width - bg_size) // 2
        logo_y = qr_y + (qr_height - bg_size) // 2
        new_img.paste(bg, (logo_x, logo_y), bg)

    # Ensure the output path has a valid file extension
    if not output_path.lower().endswith('.png'):
        output_path += '.png'
    
    new_img.save(output_path)
    print(f"二维码已生成并保存到 {output_path}")

# 示例使用
if __name__ == "__main__":
    url = "http://oa.honess.cn/spa/workflow/static4mobileform/index.html#/req?iscreate=1&workflowid=719525&yyxmmc=686235&gyd=26&xjlx=1"
    title = "山西晋泓环保华昱运营项目"
    top_text = "1-集水井"
    output_file = "my_qrcode.png"
    logo_file = "logo.png"  # 请替换为你的logo图片路径
    create_qr_with_title(url, title, output_file, font_size=30, padding=15, top_text=top_text, logo_path=logo_file, logo_scale=0.18)

    try:
        img = Image.open(output_file)
        img.show()
    except:
        print(f"无法自动显示图片，请手动打开 {output_file}")