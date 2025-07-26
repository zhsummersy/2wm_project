import requests
import json

def test_generate_qr_package():
    # 定义测试数据
    data = {
        "qr_list": [
            {
                "title": "测试标题1",
                "content": "测试内容1",
                "url": "http://example.com/1"
            },
            {
                "title": "测试标题2",
                "content": "测试内容2",
                "url": "http://example.com/2"
            }
        ]
    }
    
    # 发送POST请求到新接口
    response = requests.post(
        'http://127.0.0.1:5000/generate_qr_package',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    
    # 检查响应状态码
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # 检查返回的内容是否为ZIP文件
    assert response.headers['Content-Type'] == 'application/zip', f"Expected Content-Type 'application/zip', but got {response.headers['Content-Type']}"
    
    # 保存返回的ZIP文件
    with open('test_qr_package.zip', 'wb') as f:
        f.write(response.content)
    
    print("测试成功，ZIP文件已保存为 test_qr_package.zip")

if __name__ == "__main__":
    test_generate_qr_package()