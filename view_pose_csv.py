import argparse
import pandas as pd
import folium
from folium import plugins
import os
from datetime import datetime
from branca.element import Figure, Element
import reverse_geocoder as rg
import json

def read_pose_csv(csv_path):
    """读取CSV文件"""
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    
    # 重命名列
    if len(df.columns) == 4:  # 假设CSV有4列：图片名、经度、纬度、高度
        df.columns = ['image_name', 'longitude', 'latitude', 'altitude']
    
    # 打印数据信息
    print("\n数据前5行：")
    print(df.head())
    print("\n数据范围：")
    print(df.describe())
    
    return df

def extract_capture_time(image_name):
    """从DJI图片文件名中提取拍摄时间
    文件名格式: DJI_YYYYMMDDHHMMSS_XXXX.JPG
    """
    try:
        # 提取时间部分 (YYYYMMDDHHMMSS)
        time_str = image_name.split('_')[1]
        # 解析时间
        year = time_str[0:4]
        month = time_str[4:6]
        day = time_str[6:8]
        return f"{year}年{month}月{day}日"
    except:
        return "未知时间"

def load_location_maps():
    """加载位置映射文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    
    try:
        with open(os.path.join(data_dir, 'province_map.json'), 'r', encoding='utf-8') as f:
            province_map = json.load(f)
        with open(os.path.join(data_dir, 'city_map.json'), 'r', encoding='utf-8') as f:
            city_map = json.load(f)
        return province_map, city_map
    except Exception as e:
        print(f"加载位置映射文件出错: {str(e)}")
        return {}, {}

def get_location_info(longitude, latitude):
    """使用reverse_geocoder获取位置信息"""
    try:
        # 加载位置映射
        province_map, city_map = load_location_maps()
        
        # 使用reverse_geocoder查询位置
        result = rg.search((latitude, longitude))[0]
        print(f"Debug - 原始返回数据: {result}")  # 添加调试信息
        
        # 获取并转换省份名称
        province = province_map.get(result['admin1'], result['admin1'])
        
        # 获取并转换城市名称
        city = city_map.get(result['name'], result['name'])
        
        # 检查转换结果
        print(f"Debug - 转换后数据: province={province}, city={city}")  # 添加调试信息
        
        # 回格式化的位置信息（添加空格）
        if result['cc'] == 'CN':
            if province in province_map.values():  # 如果已经是中文省份名
                return f"中国 {province}省 {city}市"
            else:  # 如果还是英文省份名
                print(f"Warning: 未找到省份 '{result['admin1']}' 的中文映射")
                return f"中国 {province} {city}市"
        elif result['cc'] == 'HK':
            return f"中国 香港特别行政区 {city}"
        elif result['cc'] == 'MO':
            return f"中国 澳门特别行政区 {city}"
        elif result['cc'] == 'TW':
            return f"中国 台湾省 {city}市"
        else:
            return f"{result['cc']} {province} {city}"
            
    except Exception as e:
        print(f"获取位置信息出错: {str(e)}")
        print(f"原始数据: {result}")  # 添加调试信息
        return "位置信息获取失败"

def add_location_info(m, longitude, latitude):
    """添加位置信息到地图左下角"""
    # 获取地理位置信息
    location = get_location_info(longitude, latitude)
    
    # 将经纬度转换为度分秒格式
    def decimal_to_dms(decimal):
        degrees = int(decimal)
        minutes_decimal = abs(decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = round((minutes_decimal - minutes) * 60, 2)
        return degrees, minutes, seconds

    # 转换经纬度
    lon_d, lon_m, lon_s = decimal_to_dms(longitude)
    lat_d, lat_m, lat_s = decimal_to_dms(latitude)
    
    # 格式化位置信息，使用 Unicode 转义序列
    coords_text = f"东经 {lon_d}\u00b0{lon_m}\u2032{lon_s}\u2033, 北纬 {lat_d}\u00b0{lat_m}\u2032{lat_s}\u2033"
    
    location_div = Element(f"""
        <div style="
            position: fixed;
            bottom: 10px;
            left: 10px;
            z-index: 1000;
            background-color: white;
            padding: 5px;
            border-radius: 5px;
            font-size: 12px;
            font-family: Arial;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
        ">
            当前位置：{location}<br>
            坐标：{coords_text}
        </div>
    """.encode('utf-8').decode('utf-8'))
    
    m.get_root().html.add_child(location_div)

def visualize_on_map(df, csv_path):
    """使用folium在地图上可视化相机位置"""
    try:
        # 生成输出HTML文件路径（与CSV文件同目录）
        csv_dir = os.path.dirname(os.path.abspath(csv_path))
        csv_name = os.path.splitext(os.path.basename(csv_path))[0]
        output_html = os.path.join(csv_dir, f"{csv_name}_map.html")
        
        # 计算中心点
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # 创建地图，使用高德地图作为默认底图
        m = folium.Map(location=[center_lat, center_lon], 
                      zoom_start=18,
                      tiles=None)  # 先不添加底图
        
        # 添加高德地图（默认）
        folium.TileLayer(
            tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
            attr='高德地图',
            name='高德地图',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加高德卫星图
        folium.TileLayer(
            tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
            attr='高德卫星',
            name='高德卫星图',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加天地图
        folium.TileLayer(
            tiles='http://t3.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=你的天地图密钥',
            attr='��地图',
            name='天地图',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加OpenStreetMap
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加Google矢量地图（显示道路和地名）
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google Maps',
            name='Google 矢量地图',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加Google卫星影像（显示实际地形）
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Google 卫星影像',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 添加位信息（不再需要API密钥）
        add_location_info(m, center_lon, center_lat)
        
        # 创建特征组来存储所有点
        feature_group = folium.FeatureGroup(name="相机位置")
        
        # 添加每个点到地图
        for idx, row in df.iterrows():
            # 创建弹出信息
            popup_text = f"""
            图片: {row['image_name']}<br>
            经度: {row['longitude']:.6f}<br>
            纬度: {row['latitude']:.6f}<br>
            高度: {row['altitude']:.2f}m
            """
            
            # 添加标记
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                popup=popup_text,
                color='red',
                fill=True,
                fill_color='red'
            ).add_to(feature_group)
        
        # 添加相机轨迹
        coordinates = df[['latitude', 'longitude']].values.tolist()
        folium.PolyLine(
            coordinates,
            weight=2,
            color='blue',
            opacity=0.8
        ).add_to(feature_group)
        
        # 添加特征组到地���
        feature_group.add_to(m)
        
        # 添加图层控制
        folium.LayerControl().add_to(m)
        
        # 添加全屏控制
        plugins.Fullscreen().add_to(m)
        
        # 添加鼠标位置示
        plugins.MousePosition().add_to(m)
        
        # 添加绘图工具
        plugins.Draw().add_to(m)
        
        # 添加测量工具
        plugins.MeasureControl(position='topleft').add_to(m)
        
        # 保存地图
        m.save(output_html)
        print(f"\n地图已保存到：{output_html}")
        print("请在浏览器中打开该件查看交互式地图")
        
    except Exception as e:
        print(f"\n错误：{str(e)}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='在地图上可视化GPS轨迹')
    parser.add_argument('csv_path', help='CSV文件路径')
    args = parser.parse_args()
    
    # 读取CSV文件
    df = read_pose_csv(args.csv_path)
    
    # 在地图上可视化
    visualize_on_map(df, args.csv_path)

if __name__ == "__main__":
    main()