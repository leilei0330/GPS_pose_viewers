# 照片GPS可视化工具
一个用于从照片中提取GPS信息并在地图上可视化的工具。

## 安装

1. 克隆此仓库：
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. 创建conda环境：
   ```bash
   conda create --name photo-gps-env python=3.9
   ```

3. 激活conda环境：
   ```bash
   conda activate photo-gps-env
   ```

4. 安装所需的包：
   ```bash
   pip install -r requirements.txt
   ```

## 脚本

### 脚本1: `extract_gps.py`
- **功能**: 从照片中提取GPS信息。
- **用法**:
  ```bash
  python extract_gps.py <photo-directory>
  ```
- **实现逻辑**: 
  该脚本使用Pillow库读取照片的EXIF数据，提取其中的GPS信息。通过解析EXIF数据中的GPS标签，获取经纬度信息。
- **技巧**: 
  确保照片包含EXIF数据，尤其是GPS信息。可以使用相机或手机拍摄时开启定位功能。

### 脚本2: `visualize_gps.py`
- **功能**: 在地图上可视化GPS数据。
- **用法**:
  ```bash
  python visualize_gps.py <gps-data-file>
  ```
- **实现逻辑**: 
  该脚本使用Folium库将GPS数据绘制在地图上。通过读取GPS数据文件，生成地图并在相应位置标记。
- **技巧**: 
  使用Folium的不同图层和标记功能，可以自定义地图的样式和标记的外观。确保GPS数据文件格式正确，通常为CSV或JSON格式。