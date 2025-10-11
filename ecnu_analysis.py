import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 设置中文字体显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

class UniversityAnalyzer:
    def __init__(self, data_dir="data/data"):
        self.data_dir = data_dir
        self.university_name = "EAST CHINA NORMAL UNIVERSITY"
        self.university_data = {}  # 存储各学科数据
        self.disciplines = []  # 所有学科列表
        
    def load_data(self):
        """加载所有学科数据，处理嵌套在"data"字段下的结构"""
        if not os.path.exists(self.data_dir):
            print(f"数据目录不存在: {self.data_dir}")
            return False
            
        # 获取所有学科数据文件
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                discipline = filename.replace(".json", "").replace("_", " ").title()
                self.disciplines.append(discipline)
                
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 提取"data"字段下的数组数据
                        items = data.get("data", [])
                        
                        # 查找华东师范大学的数据
                        for item in items:
                            if item.get("institution") == self.university_name:
                                if discipline not in self.university_data:
                                    self.university_data[discipline] = []
                                self.university_data[discipline].append(item)
                                
                except Exception as e:
                    print(f"加载文件 {filename} 时出错: {str(e)}")
        
        return len(self.university_data) > 0
    
    def generate_report(self, output_file="华东师范大学学科分析报告.html"):
        """生成分析报告，同时处理数值类型转换（因为JSON中数值是字符串）"""
        if not self.university_data:
            print("没有找到华东师范大学的数据，无法生成报告")
            return
        
        # 创建报告内容
        report_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>华东师范大学学科情况分析报告</title>
    <style>
        body {{ font-family: SimHei, Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .discipline {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .metric {{ display: inline-block; width: 30%; margin: 10px 1%; padding: 10px; background-color: #ecf0f1; border-radius: 4px; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>华东师范大学学科情况分析报告</h1>
    <p>报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>摘要</h2>
        <p>本报告分析了华东师范大学在{', '.join(self.university_data.keys())}等学科的表现，
        主要从论文数量、被引次数、顶尖论文数量等指标进行分析。</p>
    </div>
"""

        # 生成各学科详细分析
        for discipline, items in self.university_data.items():
            # 转换为DataFrame以便分析，同时将字符串类型的数值转换为浮点型或整型
            df = pd.DataFrame(items)
            
            # 定义需要转换的数值列及其类型（根据实际情况调整）
            numeric_cols = {
                'hotPapers': int, 'citesHotPapers': int, 'citesHighPapers': int,
                'totalCount': int, 'topPapers': int, 'wosDocs': int, 'cites': int,
                'citesTopPapers': int, 'highPapers': int,
                'citesPerHighPaper': float, 'citesPerHotPaper': float, 
                'citesPerTopPaper': float, 'citesPerPaper': float
            }
            
            for col, dtype in numeric_cols.items():
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
            
            # 计算汇总统计
            total_papers = df['wosDocs'].sum() if 'wosDocs' in df.columns else 0
            total_citations = df['cites'].sum() if 'cites' in df.columns else 0
            top_papers = df['topPapers'].sum() if 'topPapers' in df.columns else 0
            avg_citations_per_paper = df['citesPerPaper'].mean() if 'citesPerPaper' in df.columns else 0
            
            # 添加学科分析到报告
            report_content += f"""
    <div class="discipline">
        <h2>{discipline}</h2>
        
        <div class="metrics">
            <div class="metric">
                <h3>总论文数</h3>
                <p>{total_papers:,}</p>
            </div>
            <div class="metric">
                <h3>总被引次数</h3>
                <p>{total_citations:,}</p>
            </div>
            <div class="metric">
                <h3>顶尖论文数</h3>
                <p>{top_papers}</p>
            </div>
            <div class="metric">
                <h3>平均每篇论文被引次数</h3>
                <p>{avg_citations_per_paper:.2f}</p>
            </div>
        </div>
    </div>
"""
            # 生成图表
            self._generate_charts(discipline, df)
            
            # 添加图表到报告
            report_content += f"""
        <div class="chart">
            <h3>{discipline}学科关键指标图表</h3>
            <img src="{discipline.replace(' ', '_')}_metrics.png" alt="{discipline}指标图" style="max-width: 800px;">
        </div>
"""

        # 完成报告内容
        report_content += """
    <div class="conclusion">
        <h2>结论</h2>
        <p>华东师范大学在多个学科领域展现了一定的研究实力。从数据来看，
        学校在顶尖论文数量和总被引次数方面有不错表现，显示出其研究成果的影响力。
        不同学科发展较为均衡，各有优势领域。</p>
    </div>
</body>
</html>
"""
        
        # 保存报告文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已生成: {output_file}")
    
    def _generate_charts(self, discipline, df):
        """生成各学科的可视化图表，适配数值列"""
        # 创建一个包含多个子图的图表
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{discipline}学科表现指标', fontsize=16)
        
        # 1. 论文数量与被引次数对比
        if 'wosDocs' in df.columns and 'cites' in df.columns:
            ax1 = axes[0, 0]
            bars = ax1.bar(['总论文数', '总被引次数'], 
                          [df['wosDocs'].sum(), df['cites'].sum()],
                          color=['#3498db', '#e74c3c'])
            ax1.set_title('论文数量与被引次数')
            ax1.bar_label(bars, fmt='%.0f')
        
        # 2. 顶尖论文与热门论文数量
        if 'topPapers' in df.columns and 'hotPapers' in df.columns and 'highPapers' in df.columns:
            ax2 = axes[0, 1]
            bars = ax2.bar(['顶尖论文', '高影响力论文', '热门论文'], 
                          [df['topPapers'].sum(), df['highPapers'].sum(), df['hotPapers'].sum()],
                          color=['#2ecc71', '#f39c12', '#9b59b6'])
            ax2.set_title('优质论文数量分布')
            ax2.bar_label(bars, fmt='%.0f')
        
        # 3. 平均每篇论文被引次数
        if 'citesPerPaper' in df.columns:
            ax3 = axes[1, 0]
            ax3.hist(df['citesPerPaper'], bins=10, color='#1abc9c')
            ax3.axvline(df['citesPerPaper'].mean(), color='r', linestyle='dashed', linewidth=1,
                       label=f'平均值: {df["citesPerPaper"].mean():.2f}')
            ax3.set_title('每篇论文被引次数分布')
            ax3.legend()
        
        # 4. 顶尖论文被引情况
        if 'citesTopPapers' in df.columns and 'topPapers' in df.columns:
            ax4 = axes[1, 1]
            if df['topPapers'].sum() > 0:
                avg_cites_top = df['citesTopPapers'].sum() / df['topPapers'].sum()
                ax4.bar(['顶尖论文平均被引'], [avg_cites_top], color='#34495e')
                ax4.set_title('顶尖论文平均被引次数')
                ax4.text(0, avg_cites_top/2, f'{avg_cites_top:.2f}', ha='center', fontsize=12)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为suptitle留出空间
        
        # 保存图表
        chart_filename = f"{discipline.replace(' ', '_')}_metrics.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    analyzer = UniversityAnalyzer()
    
    # 加载数据
    if analyzer.load_data():
        print(f"成功加载华东师范大学在{len(analyzer.university_data)}个学科的数据")
        # 生成报告
        analyzer.generate_report()
    else:
        print("未能加载到华东师范大学的数据，请检查数据文件是否存在且格式正确")