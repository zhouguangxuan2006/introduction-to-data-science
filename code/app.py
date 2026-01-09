from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import requests

# 设置忽略SSL证书警告
requests.packages.urllib3.disable_warnings()

from air_quality_crawler import crawl_all_cities, get_air_quality_data

app = Flask(__name__)

# 添加CORS支持
CORS(app)

# 数据目录
DATA_DIR = "../data"

# 示例县级/镇级数据（实际应用中可从数据库或API获取）
county_data = {
    "北京": [
        {"name": "朝阳区", "lat": 39.9489, "lng": 116.4814, "aqi": 0, "pm25": 0},
        {"name": "海淀区", "lat": 40.0025, "lng": 116.3158, "aqi": 0, "pm25": 0},
        {"name": "西城区", "lat": 39.9158, "lng": 116.3667, "aqi": 0, "pm25": 0},
        {"name": "东城区", "lat": 39.9163, "lng": 116.4074, "aqi": 0, "pm25": 0},
        {"name": "丰台区", "lat": 39.8652, "lng": 116.2881, "aqi": 0, "pm25": 0}
    ],
    "上海": [
        {"name": "浦东新区", "lat": 31.2304, "lng": 121.4737, "aqi": 0, "pm25": 0},
        {"name": "徐汇区", "lat": 31.1957, "lng": 121.4357, "aqi": 0, "pm25": 0},
        {"name": "黄浦区", "lat": 31.2317, "lng": 121.4726, "aqi": 0, "pm25": 0},
        {"name": "静安区", "lat": 31.2350, "lng": 121.4586, "aqi": 0, "pm25": 0},
        {"name": "长宁区", "lat": 31.2197, "lng": 121.4207, "aqi": 0, "pm25": 0}
    ],
    "广州": [
        {"name": "天河区", "lat": 23.1201, "lng": 113.3249, "aqi": 0, "pm25": 0},
        {"name": "越秀区", "lat": 23.1353, "lng": 113.2644, "aqi": 0, "pm25": 0},
        {"name": "海珠区", "lat": 23.0975, "lng": 113.2516, "aqi": 0, "pm25": 0},
        {"name": "白云区", "lat": 23.2178, "lng": 113.2576, "aqi": 0, "pm25": 0},
        {"name": "番禺区", "lat": 22.9499, "lng": 113.3996, "aqi": 0, "pm25": 0}
    ],
    "深圳": [
        {"name": "南山区", "lat": 22.5333, "lng": 113.9306, "aqi": 0, "pm25": 0},
        {"name": "福田区", "lat": 22.5431, "lng": 114.0579, "aqi": 0, "pm25": 0},
        {"name": "罗湖区", "lat": 22.5429, "lng": 114.1055, "aqi": 0, "pm25": 0},
        {"name": "宝安区", "lat": 22.5470, "lng": 113.8511, "aqi": 0, "pm25": 0},
        {"name": "龙岗区", "lat": 22.6273, "lng": 114.1490, "aqi": 0, "pm25": 0}
    ],
    "成都": [
        {"name": "锦江区", "lat": 30.6537, "lng": 104.0718, "aqi": 0, "pm25": 0},
        {"name": "青羊区", "lat": 30.6761, "lng": 104.0699, "aqi": 0, "pm25": 0},
        {"name": "金牛区", "lat": 30.7031, "lng": 104.0545, "aqi": 0, "pm25": 0},
        {"name": "武侯区", "lat": 30.6430, "lng": 104.0549, "aqi": 0, "pm25": 0},
        {"name": "成华区", "lat": 30.6633, "lng": 104.0881, "aqi": 0, "pm25": 0}
    ]
}

@app.route('/api/air-quality/latest', methods=['GET'])
def get_latest_air_quality():
    """
    获取最新空气质量数据
    """
    file_path = os.path.join(DATA_DIR, "latest_air_quality.csv")
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            data = df.to_dict(orient='records')
            return jsonify({
                "success": True,
                "data": data,
                "message": "获取数据成功"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"读取数据失败：{str(e)}"
            })
    else:
        return jsonify({
            "success": False,
            "message": "暂无数据，请先运行爬虫"
        })

@app.route('/api/air-quality/city/<string:city>', methods=['GET'])
def get_city_air_quality(city):
    """
    获取指定城市的空气质量数据
    """
    # 尝试从CSV文件获取
    file_path = os.path.join(DATA_DIR, "latest_air_quality.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        city_data = df[df['城市'] == city]
        if not city_data.empty:
            return jsonify({
                "success": True,
                "data": city_data.to_dict(orient='records')[0],
                "message": "获取数据成功"
            })
    
    # 如果CSV中没有，尝试实时爬取
    data = get_air_quality_data(city)
    if data:
        return jsonify({
            "success": True,
            "data": data,
            "message": "获取数据成功"
        })
    else:
        return jsonify({
            "success": False,
            "message": f"未找到{city}的数据"
        })

@app.route('/api/air-quality/county/<string:city>', methods=['GET'])
def get_county_air_quality(city):
    """
    获取指定城市的县级/镇级空气质量数据
    """
    if city in county_data:
        # 获取城市的AQI数据作为基础
        city_aqi = 100  # 默认值
        
        # 尝试从CSV文件获取城市AQI
        file_path = os.path.join(DATA_DIR, "latest_air_quality.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                city_data = df[df['城市'] == city]
                if not city_data.empty:
                    city_aqi = city_data.iloc[0]['AQI']
            except Exception as e:
                print(f"读取城市AQI数据失败: {str(e)}")
        
        # 生成动态县级数据
        dynamic_county_data = county_data[city].copy()
        for i in range(len(dynamic_county_data)):
            # 根据城市AQI生成县级AQI，波动范围±20
            import random
            county_aqi = max(0, city_aqi + random.randint(-20, 20))
            
            # 根据AQI生成PM2.5数据
            county_pm25 = int(county_aqi * 0.6 + random.randint(-10, 10))
            
            # 更新县级数据
            dynamic_county_data[i]['aqi'] = county_aqi
            dynamic_county_data[i]['pm25'] = county_pm25
        
        return jsonify({
            "success": True,
            "data": dynamic_county_data,
            "message": "获取数据成功"
        })
    else:
        return jsonify({
            "success": False,
            "message": f"未找到{city}的县级数据"
        })

@app.route('/api/air-quality/update', methods=['POST'])
def update_air_quality():
    """
    手动触发数据更新
    """
    try:
        # 爬取最新数据
        air_quality_data = crawl_all_cities()
        
        if air_quality_data:
            return jsonify({
                "success": True,
                "message": f"成功更新{len(air_quality_data)}个城市的数据"
            })
        else:
            return jsonify({
                "success": False,
                "message": "更新失败，未获取到数据"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败：{str(e)}"
        })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """
    获取支持的城市列表
    """
    file_path = os.path.join(DATA_DIR, "latest_air_quality.csv")
    cities = []
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        cities = df['城市'].tolist()
    
    return jsonify({
        "success": True,
        "data": cities,
        "message": "获取城市列表成功"
    })

@app.route('/', methods=['GET'])
def index():
    """
    首页
    """
    return "空气质量数据API服务运行中"

if __name__ == '__main__':
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
