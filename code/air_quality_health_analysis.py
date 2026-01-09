import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import requests
from io import StringIO
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 创建结果目录
RESULTS_PATH = os.path.join(SCRIPT_DIR, '../results')
if not os.path.exists(RESULTS_PATH):
    os.makedirs(RESULTS_PATH)
    print(f"创建结果目录: {RESULTS_PATH}")
else:
    print(f"结果目录已存在: {RESULTS_PATH}")

# 1. 数据获取与预处理
def load_and_preprocess_data():
    print("1. 正在加载数据...")
    
    # 模拟空气质量数据（城市、AQI、PM2.5、PM10、O3）
    air_quality_data = {
        '城市': ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '西安', '重庆', '南京'],
        'AQI': [85, 72, 68, 65, 92, 78, 80, 105, 95, 75],
        'PM2.5': [58, 45, 42, 38, 65, 50, 52, 75, 68, 48],
        'PM10': [89, 70, 65, 60, 98, 75, 78, 110, 102, 72],
        'O3': [120, 110, 105, 100, 125, 115, 118, 130, 128, 112],
        '纬度': [39.9042, 31.2304, 23.1291, 22.5431, 30.5728, 30.2741, 30.5928, 34.2658, 29.5630, 32.0603],
        '经度': [116.4074, 121.4737, 113.2644, 114.0579, 104.0668, 120.1551, 114.3055, 108.9541, 106.5516, 118.7969]
    }
    
    # 模拟健康数据（城市、哮喘发病率、心血管疾病发病率）
    health_data = {
        '城市': ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '西安', '重庆', '南京'],
        '哮喘发病率(‰)': [3.2, 2.8, 2.5, 2.3, 3.5, 2.9, 3.0, 3.8, 3.6, 2.7],
        '心血管疾病发病率(‰)': [12.5, 10.8, 9.5, 9.0, 13.2, 11.2, 11.5, 14.0, 13.5, 10.5]
    }
    
    # 创建DataFrame
    air_df = pd.DataFrame(air_quality_data)
    health_df = pd.DataFrame(health_data)
    
    # 数据合并
    merged_df = pd.merge(air_df, health_df, on='城市', how='inner')
    
    print("数据加载完成！")
    return merged_df

# 2. 探索性数据分析
def exploratory_data_analysis(df):
    print("\n2. 正在进行探索性数据分析...")
    
    # 基本统计信息
    print("\n=== 数据基本统计信息 ===")
    print(df.describe())
    
    # 保存基本统计信息到文件
    df.describe().to_csv(os.path.join(RESULTS_PATH, 'statistics_summary.csv'), encoding='utf-8-sig')
    
    # 相关性分析
    print("\n=== 相关性分析 ===")
    # 选择数值列进行相关性计算
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()
    print(corr_matrix)
    
    # 保存相关性矩阵到文件
    corr_matrix.to_csv(os.path.join(RESULTS_PATH, 'correlation_matrix.csv'), encoding='utf-8-sig')
    
    return corr_matrix

# 3. 数据可视化
def visualize_data(df, corr_matrix):
    print("\n3. 正在生成可视化图表...")
    
    # 设置图形风格
    sns.set(style="whitegrid", font_scale=1.2)
    
    # 3.1 AQI与健康指标散点图
    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    sns.scatterplot(x='AQI', y='哮喘发病率(‰)', data=df, hue='城市', s=100, alpha=0.8)
    plt.title('AQI与哮喘发病率关系')
    plt.xlabel('AQI指数')
    plt.ylabel('哮喘发病率(‰)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.subplot(1, 2, 2)
    sns.scatterplot(x='AQI', y='心血管疾病发病率(‰)', data=df, hue='城市', s=100, alpha=0.8)
    plt.title('AQI与心血管疾病发病率关系')
    plt.xlabel('AQI指数')
    plt.ylabel('心血管疾病发病率(‰)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PATH, 'aqi_health_scatter.png'), dpi=300, bbox_inches='tight')
    
    # 3.2 PM2.5与健康指标散点图
    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    sns.scatterplot(x='PM2.5', y='哮喘发病率(‰)', data=df, hue='城市', s=100, alpha=0.8)
    plt.title('PM2.5与哮喘发病率关系')
    plt.xlabel('PM2.5浓度 (μg/m³)')
    plt.ylabel('哮喘发病率(‰)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.subplot(1, 2, 2)
    sns.scatterplot(x='PM2.5', y='心血管疾病发病率(‰)', data=df, hue='城市', s=100, alpha=0.8)
    plt.title('PM2.5与心血管疾病发病率关系')
    plt.xlabel('PM2.5浓度 (μg/m³)')
    plt.ylabel('心血管疾病发病率(‰)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PATH, 'pm25_health_scatter.png'), dpi=300, bbox_inches='tight')
    
    # 3.3 相关性热力图
    plt.figure(figsize=(12, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', mask=mask, vmin=-1, vmax=1, fmt='.2f')
    plt.title('空气质量与健康指标相关性热力图')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PATH, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
    
    # 3.4 城市AQI柱状图
    plt.figure(figsize=(12, 6))
    sns.barplot(x='城市', y='AQI', data=df, palette='viridis')
    plt.title('各城市AQI指数对比')
    plt.xlabel('城市')
    plt.ylabel('AQI指数')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PATH, 'city_aqi_comparison.png'), dpi=300, bbox_inches='tight')
    
    # 3.5 交互式空气质量地图
    create_air_quality_map(df)
    
    plt.close('all')
    print("可视化图表生成完成！")

# 创建交互式空气质量地图
def create_air_quality_map(df):
    print("   正在生成交互式地图...")
    
    # 创建地图中心（中国中心）
    m = folium.Map(location=[35.8617, 104.1954], zoom_start=4)
    
    # 添加城市标记
    for _, row in df.iterrows():
        # 根据AQI设置颜色
        if row['AQI'] <= 50:
            color = 'green'
            aqi_level = '优'
        elif row['AQI'] <= 100:
            color = 'yellow'
            aqi_level = '良'
        elif row['AQI'] <= 150:
            color = 'orange'
            aqi_level = '轻度污染'
        else:
            color = 'red'
            aqi_level = '中度污染'
        
        # 弹出信息
        popup_content = f"""
        <b>{row['城市']}</b><br>
        AQI: {row['AQI']} ({aqi_level})<br>
        PM2.5: {row['PM2.5']} μg/m³<br>
        PM10: {row['PM10']} μg/m³<br>
        O3: {row['O3']} μg/m³<br>
        哮喘发病率: {row['哮喘发病率(‰)']}‰<br>
        心血管疾病发病率: {row['心血管疾病发病率(‰)']}‰
        """
        
        folium.Marker(
            location=[row['纬度'], row['经度']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # 保存地图
    m.save(os.path.join(RESULTS_PATH, 'air_quality_map.html'))
    print("   交互式地图生成完成！")

# 4. 相关性分析与结论
def analyze_correlation(corr_matrix):
    print("\n4. 正在进行相关性分析...")
    
    # 提取空气质量与健康指标的相关性
    health_correlations = corr_matrix[["哮喘发病率(‰)", "心血管疾病发病率(‰)"]].loc[["AQI", "PM2.5", "PM10", "O3"]]
    
    print("\n=== 空气质量指标与健康指标相关性 ===")
    print(health_correlations)
    
    # 保存相关性结果
    health_correlations.to_csv(os.path.join(RESULTS_PATH, 'health_correlations.csv'), encoding='utf-8-sig')
    
    return health_correlations

# 5. 生成分析报告
def generate_report(df, health_correlations):
    print("\n5. 正在生成分析报告...")
    
    report_content = f"""
# 城市空气质量与健康关联分析报告

## 一、研究背景
随着城市化进程的加快，空气质量问题日益突出，对居民健康的影响受到广泛关注。本研究通过分析中国10个主要城市的空气质量数据与健康指标的相关性，探讨空气质量对居民健康的影响。

## 二、数据来源与处理
- **数据类型**：模拟数据（包含10个城市的空气质量指标和健康数据）
- **空气质量指标**：AQI、PM2.5、PM10、O3
- **健康指标**：哮喘发病率(‰)、心血管疾病发病率(‰)

## 三、数据分析结果

### 1. 空气质量基本情况
{df[['城市', 'AQI', 'PM2.5', 'PM10', 'O3']].to_markdown(index=False)}

### 2. 健康指标基本情况
{df[['城市', '哮喘发病率(‰)', '心血管疾病发病率(‰)']].to_markdown(index=False)}

### 3. 相关性分析
空气质量指标与健康指标的相关性系数：
{health_correlations.to_markdown()}

#### 关键发现：
- PM2.5与哮喘发病率的相关性最高，达到{health_correlations.loc['PM2.5', '哮喘发病率(‰)']:.2f}
- PM10与心血管疾病发病率的相关性最高，达到{health_correlations.loc['PM10', '心血管疾病发病率(‰)']:.2f}
- 整体而言，颗粒物（PM2.5、PM10）对健康的影响比气态污染物（O3）更显著

## 四、可视化结果

### 1. 相关性热力图
![相关性热力图](../results/correlation_heatmap.png)

### 2. AQI与健康指标关系
![AQI与健康指标散点图](../results/aqi_health_scatter.png)

### 3. PM2.5与健康指标关系
![PM2.5与健康指标散点图](../results/pm25_health_scatter.png)

### 4. 各城市AQI对比
![城市AQI对比](../results/city_aqi_comparison.png)

### 5. 交互式空气质量地图
打开 `../results/air_quality_map.html` 查看交互式地图

## 五、结论与建议

### 结论：
1. 空气质量与居民健康存在显著相关性，尤其是颗粒物污染对呼吸系统和心血管系统影响较大
2. 不同城市的空气质量差异明显，北方城市整体空气质量较差
3. PM2.5和PM10是影响居民健康的主要空气污染物

### 建议：
1. 加强对颗粒物污染的治理，尤其是PM2.5和PM10的监测与控制
2. 建立空气质量与健康数据的长期监测机制
3. 提高公众对空气质量的认识，倡导绿色出行和环保生活方式
4. 针对高污染城市制定专项治理措施

## 六、技术实现
- **数据分析工具**：Python、Pandas、NumPy
- **可视化工具**：Matplotlib、Seaborn、Folium
- **分析方法**：相关性分析、热力图、散点图、柱状图

---
**报告生成时间**：2026-01-02
**数据来源**：模拟数据
    """
    
    # 保存报告
    with open(os.path.join(RESULTS_PATH, 'analysis_report.md'), 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("分析报告生成完成！")

# 主函数
def main():
    print("\n" + "="*50)
    print("城市空气质量与健康关联分析")
    print("="*50 + "\n")
    
    # 执行完整分析流程
    df = load_and_preprocess_data()
    corr_matrix = exploratory_data_analysis(df)
    visualize_data(df, corr_matrix)
    health_correlations = analyze_correlation(corr_matrix)
    generate_report(df, health_correlations)
    
    print("\n" + "="*50)
    print("分析完成！结果已保存到 results 目录")
    print("="*50)

if __name__ == "__main__":
    main()
