-- 测试数据插入脚本
-- 表结构: id, title, content, url, img_url

-- 清空现有数据（可选）
-- DELETE FROM qr_info;

-- 插入测试数据
INSERT INTO qr_info (title, content, url, img_url) VALUES 
('测试标题1', '测试内容1', 'http://example.com/1', 'test1.png'),
('测试标题2', '测试内容2', 'http://example.com/2', 'test2.png'),
('测试标题3', '测试内容3', 'http://example.com/3', 'test3.png'),
('测试标题4', '测试内容4', 'http://example.com/4', 'test4.png'),
('测试标题5', '测试内容5', 'http://example.com/5', 'test5.png')
-- 验证数据插入
SELECT * FROM qr_info;