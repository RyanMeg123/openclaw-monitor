import re

# 读取文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换 base64 图片为带有 id 的 img 标签
# 匹配 data:image/jpeg;base64,... 这种格式的图片
pattern = r'<img[^>]*src="data:image[^"]*"[^>]*>'

# 替换为新的 img 标签，添加 id 以便 JS 控制
replacement = '<img id="screenshot-img" src="image-cn.png" class="screenshot-img">'

new_content = re.sub(pattern, replacement, content)

# 保存文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 已替换 base64 图片为本地图片路径")

# 现在添加语言切换时切换图片的 JavaScript 代码
# 找到 setLang 函数，在末尾添加图片切换逻辑

# 读取文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 setLang 函数末尾添加图片切换代码
# 找到 "// Initialize" 这一行，在它之前插入图片切换代码

js_code = '''      // Update screenshot image
      const screenshotImg = document.getElementById('screenshot-img');
      if (screenshotImg) {
        screenshotImg.src = lang === 'zh' ? 'image-cn.png' : 'image.png';
      }
      
'''

# 在 "// Initialize" 之前插入代码
content = content.replace('      // Initialize', js_code + '      // Initialize')

# 保存文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已添加语言切换时图片切换功能")
