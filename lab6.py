import os
import pandas as pd
import sqlite3
import logging
import numpy as np
from typing import Optional, Tuple
from sklearn.cluster import KMeans
# 导入所需的特征工程和模型库
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.neural_network import MLPRegressor 
from sklearn.metrics import mean_squared_error, r2_score
from scipy.spatial.distance import cdist
# 关键修改：导入 train_test_split 用于随机划分数据
from sklearn.model_selection import train_test_split 

# ==============================================================================
# 1. 配置和初始化 (路径已根据您的要求修改)
# ==============================================================================

CONFIG = {
    # 原始 CSV 数据文件的【输入】目录 (lab4\download)
    "data_dir": r"D:\vsc\数据科学与大数据技术导论\lab4\download", 
    # **【用户指定输出目录】**：分析结果、日志和数据库文件的【输出】目录 (lab6)
    "output_dir": r"D:\vsc\数据科学与大数据技术导论\lab6", 
    
    # 数据库文件名 (将保存在 output_dir)
    "db_name": "university_ranking.db",
    # 最终 Excel 输出文件名
    "output_filename": "analysis_results_lab6.xlsx",
    
    "target_institution": "EAST CHINA NORMAL UNIVERSITY", 
    "target_country": "CHINA MAINLAND",                  
    "csv_encodings": ["utf-8", "gbk", "latin1"],
}

# 确保输出目录存在
if not os.path.exists(CONFIG["output_dir"]):
    os.makedirs(CONFIG["output_dir"]) 

# 构建输出文件的完整路径
log_path = os.path.join(CONFIG["output_dir"], "analysis.log")

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path, encoding='utf-8') 
    ]
)
logger = logging.getLogger(__name__)

# 规范化列名映射
COLUMN_MAPPING = {
    'Institutions': 'institution',
    'Countries/Regions': 'country',
    'Web of Science Documents': 'documents',
    'Cites': 'cites',
    'Cites/Paper': 'cites_per_paper',
    'Top Papers': 'top_papers',
}

# 数据库列名和类型
DB_COLUMNS = {
    'subject': 'TEXT',
    'rank': 'INTEGER',
    'institution': 'TEXT',
    'country': 'TEXT',
    'documents': 'REAL', 
    'cites': 'REAL',
    'cites_per_paper': 'REAL',
    'top_papers': 'REAL',
}


# ==============================================================================
# 2. 辅助函数：自定义 MAPE
# ==============================================================================

def mean_absolute_percentage_error(y_true, y_pred):
    """计算平均绝对百分比误差 (MAPE)。"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    epsilon = 1e-10 
    return np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100


# ==============================================================================
# 3. 数据加载和分析函数 (保持不变)
# ==============================================================================

def init_database(conn: sqlite3.Connection) -> None:
    """初始化数据库表结构"""
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS rankings")
        columns_sql = ",\n".join([f"{col} {dtype}" for col, dtype in DB_COLUMNS.items()])
        create_table_sql = f"CREATE TABLE rankings (\n{columns_sql}\n)"
        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("数据库表结构初始化成功。")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}", exc_info=True)
        raise


def load_all_csvs(data_dir: str, conn: sqlite3.Connection) -> None:
    """读取所有CSV文件，清洗并写入数据库"""
    
    if not os.path.isdir(data_dir):
        logger.error(f"数据目录不存在: {data_dir}")
        return

    total_files = 0
    success_files = 0
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            total_files += 1
            file_path = os.path.join(data_dir, filename)
            research_subject = os.path.splitext(filename)[0]

            df: Optional[pd.DataFrame] = None
            for encoding in CONFIG["csv_encodings"]:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, header=1) 
                    break 
                except Exception:
                    continue
            
            if df is None:
                logger.error(f"文件 {filename} 无法读取，跳过。")
                continue

            try:
                if df.columns[0].strip() == '1' or df.columns[0].startswith('Unnamed'):
                    df = df.iloc[:, 1:] 
                
                df.columns = [col.strip() for col in df.columns]
                new_cols = {orig: new for orig, new in COLUMN_MAPPING.items() if orig in df.columns}
                df = df.rename(columns=new_cols)
                
                df['subject'] = research_subject
                df.insert(0, 'rank', range(1, len(df) + 1)) 
                
                numeric_cols = ['documents', 'cites', 'cites_per_paper', 'top_papers']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df = df.reindex(columns=DB_COLUMNS.keys())
                
                df.to_sql("rankings", conn, if_exists="append", index=False)
                success_files += 1
                logger.info(f"成功处理文件: {filename}")

            except Exception as e:
                logger.error(f"处理文件 {filename} 时发生清洗或DB写入错误: {e}", exc_info=True)
                continue
                
    logger.info(f"数据加载完成。总文件数: {total_files}, 成功处理: {success_files}")


def get_full_df_with_stats(conn: sqlite3.Connection) -> pd.DataFrame:
    """从数据库加载数据并计算 rank_percentile"""
    query = f"SELECT {', '.join(DB_COLUMNS.keys())} FROM rankings"
    full_df = pd.read_sql_query(query, conn)
    
    df_with_percentile = []
    for subject, group_df in full_df.groupby('subject'):
        group_df['total_institutions'] = len(group_df)
        group_df['rank_percentile'] = ((group_df['total_institutions'] - group_df['rank']) / group_df['total_institutions']) * 100
        df_with_percentile.append(group_df)
    return pd.concat(df_with_percentile)


def perform_analysis(full_df_with_stats: pd.DataFrame, target_institution: str, target_country: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """执行基础的三个分析任务 (ECNU, China, Region Averages)"""
    
    # --- 1. ECNU Performance ---
    ecnu_performance = []
    for subject, group_df in full_df_with_stats.groupby('subject'):
        ecnu_row = group_df[group_df['institution'] == target_institution]
        if not ecnu_row.empty:
            ecnu_performance.append({
                'Subject': subject,
                'Rank': ecnu_row['rank'].iloc[0],
                'Total_Institutions': ecnu_row['total_institutions'].iloc[0],
                'Rank_Percentile (%)': round(ecnu_row['rank_percentile'].iloc[0], 2),
                'Cites/Paper': ecnu_row['cites_per_paper'].iloc[0],
            })
        else:
            ecnu_performance.append({
                'Subject': subject,
                'Rank': None,
                'Total_Institutions': len(group_df),
                'Rank_Percentile (%)': 0,
                'Cites/Paper': None,
            })
    ecnu_df = pd.DataFrame(ecnu_performance).sort_values(by='Rank_Percentile (%)', ascending=False).reset_index(drop=True)

    # --- 2. China Mainland Averages ---
    china_avg_df = full_df_with_stats[full_df_with_stats['country'] == target_country].groupby('subject').agg(
        Average_Cites_Per_Paper=('cites_per_paper', 'mean'),
        Average_Rank=('rank', 'mean'),
        Total_Institutions=('institution', 'size')
    ).reset_index().rename(columns={'subject': 'Subject'})
    china_avg_df['Average_Cites_Per_Paper'] = china_avg_df['Average_Cites_Per_Paper'].round(2)
    china_avg_df['Average_Rank'] = china_avg_df['Average_Rank'].round(1)
    
    # --- 3. Region Averages ---
    region_df = full_df_with_stats.groupby('country').agg(
        Average_Cites_Per_Paper=('cites_per_paper', 'mean'),
        Total_Subjects_Covered=('subject', 'nunique'),
        Total_Institutions=('institution', 'size')
    ).reset_index().rename(columns={'country': 'Country/Region'})
    region_df['Average_Cites_Per_Paper'] = region_df['Average_Cites_Per_Paper'].round(2)
    region_df = region_df.sort_values(by='Average_Cites_Per_Paper', ascending=False)
    
    return ecnu_df, china_avg_df, region_df


def analyze_clustering(full_df_with_stats: pd.DataFrame, target_institution: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """目标 8: 全球高校聚类分析"""
    logger.info("--- 目标 8: 开始聚类分析 ---")
    
    institution_df = full_df_with_stats.groupby('institution').agg(
        avg_rank_percentile=('rank_percentile', 'mean'),
        avg_cites_per_paper=('cites_per_paper', 'mean'),
        total_documents=('documents', 'sum'),
        subjects_covered=('subject', 'nunique'),
        country=('country', lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A')
    ).reset_index()

    features = ['avg_rank_percentile', 'avg_cites_per_paper', 'total_documents', 'subjects_covered']
    clustering_df = institution_df.dropna(subset=features)
    
    if len(clustering_df) < 50:
        logger.warning(f"聚类数据量不足 ({len(clustering_df)}), 无法进行有效聚类。")
        return pd.DataFrame({'Note': ['Data too sparse for clustering.']}), pd.DataFrame({'Note': ['Data too sparse for clustering.']})

    X = clustering_df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 聚类 (K=4)
    K = 4 
    kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
    clustering_df['Cluster'] = kmeans.fit_predict(X_scaled)
    institution_df = institution_df.merge(clustering_df[['institution', 'Cluster']], on='institution', how='left')
    institution_df['Cluster'] = institution_df['Cluster'].fillna(-1).astype(int)

    # 聚类总结
    cluster_summary = institution_df[institution_df['Cluster'] != -1].groupby('Cluster').agg(
        Count=('institution', 'size'),
        Avg_Rank_Percentile=('avg_rank_percentile', 'mean'),
        Avg_Cites_Per_Paper=('avg_cites_per_paper', 'mean'),
        Avg_Documents=('total_documents', 'mean'),
        Representative_Country=('country', lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A')
    ).reset_index().sort_values(by='Avg_Rank_Percentile', ascending=False)
    
    # 找出相似高校
    ecnu_row = institution_df[institution_df['institution'] == target_institution]
    if ecnu_row.empty or ecnu_row['Cluster'].iloc[0] == -1:
        logger.warning(f"目标机构 {target_institution} 未能参与聚类。")
        return cluster_summary, pd.DataFrame({'Note': [f"{target_institution} 无法参与聚类或数据缺失。"]})
        
    ecnu_cluster = ecnu_row['Cluster'].iloc[0]
    similar_schools = clustering_df[clustering_df['Cluster'] == ecnu_cluster].copy()
    
    # 计算距离 (标准化空间)
    ecnu_features = scaler.transform(ecnu_row[features].values)
    similar_schools_features = scaler.transform(similar_schools[features].values)
    distances = cdist(ecnu_features, similar_schools_features, metric='euclidean')[0]
    similar_schools['Distance_to_ECNU'] = distances
    
    similar_schools = similar_schools[similar_schools['institution'] != target_institution]
    similar_schools = similar_schools.sort_values(by='Distance_to_ECNU', ascending=True).head(10)
    
    similar_schools = similar_schools.rename(
        columns={'institution': 'Similar_Institution', 'country': 'Country'}
    )
    
    logger.info("聚类分析和相似高校分析完成。")
    return cluster_summary, similar_schools[[
        'Similar_Institution', 'Country', 'Distance_to_ECNU', 'avg_rank_percentile', 'avg_cites_per_paper'
    ]]


def analyze_ecnu_profile(full_df_with_stats: pd.DataFrame, target_institution: str) -> pd.DataFrame:
    """目标 9: ECNU 学科画像 (EDA)"""
    logger.info("--- 目标 9: 开始 ECNU 学科画像分析 ---")
    
    ecnu_df = full_df_with_stats[full_df_with_stats['institution'] == target_institution].copy()

    if ecnu_df.empty:
        return pd.DataFrame({'Note': [f"未找到 {target_institution} 的数据。"]})

    # 1. 核心指标
    profile = {
        'Total Subjects Ranked': [len(ecnu_df)],
        'Best Rank Percentile (%)': [ecnu_df['rank_percentile'].max().round(2)],
        'Worst Rank Percentile (%)': [ecnu_df['rank_percentile'].min().round(2)],
        'Median Rank Percentile (%)': [ecnu_df['rank_percentile'].median().round(2)],
        'Subjects > 90% Percentile': [(ecnu_df['rank_percentile'] > 90).sum()],
        'Average Cites/Paper': [ecnu_df['cites_per_paper'].mean().round(2)],
        'Total Documents': [ecnu_df['documents'].sum().round(0)],
        'Average Rank': [ecnu_df['rank'].mean().round(1)],
    }
    
    # 2. 相对引用指标 (RCR)
    global_avg = full_df_with_stats.groupby('subject')['cites_per_paper'].mean().reset_index().rename(columns={'cites_per_paper': 'global_avg_cites'})
    ecnu_comparison = ecnu_df[['subject', 'cites_per_paper']].merge(global_avg, on='subject', how='left')
    ecnu_comparison['RCR'] = np.where(ecnu_comparison['global_avg_cites'] != 0, 
                                     ecnu_comparison['cites_per_paper'] / ecnu_comparison['global_avg_cites'], 
                                     np.nan)
    
    profile['Subjects with RCR > 1 (Above Global Avg)'] = [(ecnu_comparison['RCR'] > 1).sum()]
    profile['Average RCR'] = [ecnu_comparison['RCR'].mean().round(2)]
    
    # 3. 强势学科列表
    top_subjects = ecnu_df.sort_values(by='rank_percentile', ascending=False).head(5)
    
    for i, row in enumerate(top_subjects.itertuples()):
        profile[f'Top Subject {i+1}'] = [f"{row.subject} (Rank: {row.rank}, Pct: {row.rank_percentile:.2f}%)"]
    
    profile_df = pd.DataFrame(profile).T.reset_index()
    profile_df.columns = ['Metric', 'Value']
    
    logger.info("ECNU 学科画像分析完成。")
    return profile_df


# ==============================================================================
# 4. 核心修改：深度学习 (MLPRegressor) 排名预测模型 (已修改为随机划分)
# ==============================================================================

def build_ranking_model(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    目标 10: 各学科排名预测模型 (使用 MLPRegressor，采用随机划分训练集，解决 R2 负值问题)
    """
    logger.info("--- 目标 10: 开始深度学习 (MLPRegressor) 排名预测建模 (随机划分) ---")
    
    model_df = full_df.dropna(subset=['rank', 'cites', 'documents', 'cites_per_paper']).copy()
    model_df = model_df[(model_df['cites'] > 1) & (model_df['documents'] > 1)].copy() 

    # 1. 特征工程 (对数变换和多项式特征)
    model_df['log_cites'] = np.log1p(model_df['cites'])
    model_df['log_documents'] = np.log1p(model_df['documents'])
    
    # 基础特征集合
    features_base = ['log_cites', 'log_documents', 'cites_per_paper']
    poly = PolynomialFeatures(degree=2, include_bias=False)
    
    results = []
    
    for subject, group_df in model_df.groupby('subject'):
        N = len(group_df)
        
        if N < 50:
            logger.warning(f"学科 {subject} (N={N}) 数据不足，跳过建模。")
            continue
        
        # 准备特征和目标
        X_base = group_df[features_base].values
        X_poly = poly.fit_transform(X_base)
        y = group_df['rank'].values

        # **【关键修改点 1】：使用 train_test_split 进行随机划分**
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_poly, y, test_size=0.2, random_state=42
        )
        
        if len(y_train) < 10 or len(y_test) < 5:
            logger.warning(f"学科 {subject} (N={N}) 划分后数据不足，跳过建模。")
            continue
            
        # 2. 标准化特征
        scaler = StandardScaler()
        # 标准化器只在训练集上 fit，然后应用于训练集和测试集
        X_train = scaler.fit_transform(X_train_raw)
        X_test = scaler.transform(X_test_raw)

        # 3. 模型：使用 MLPRegressor (神经网络)
        # **【关键修改点 2】：增强模型复杂度**
        model = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32), # 增加神经元数量
            activation='relu',
            solver='adam',
            max_iter=1000, # 增加迭代次数以保证收敛
            random_state=42,
        )
        model.fit(X_train, y_train)

        # 4. 预测与后处理
        y_pred = model.predict(X_test)
        # 排名不能小于 1，并取整
        y_pred = np.maximum(y_pred, 1).round().astype(int) 

        # 5. 评估指标
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred) 
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(y_test, y_pred) 
        
        # 准确率在 10% 误差范围内
        error_percent = np.abs(y_test - y_pred) / y_test
        accuracy_within_10_percent = (error_percent <= 0.1).mean()

        results.append({
            'Subject': subject,
            'Model_R2': round(r2, 4),
            'Model_MSE': round(mse, 2),             
            'Model_RMSE': round(rmse, 2),
            'Model_MAPE': f"{round(mape, 2)}%",     
            'Test_Size': len(y_test),
            'Accuracy_Within_10%': f"{round(accuracy_within_10_percent * 100, 2)}%",
        })

    model_summary_df = pd.DataFrame(results).sort_values(by='Model_R2', ascending=False)
    logger.info("深度学习排名预测模型分析完成。")
    return model_summary_df

# ==============================================================================
# 5. 结果导出和主流程 (路径已修改)
# ==============================================================================

def export_all_results(output_path, *dfs) -> None:
    """将所有分析结果导出到Excel文件"""
    
    sheet_names = [
        "1_ECNU_Basic_Performance", "2_China_Averages", "3_Region_Averages",
        "4_Clustering_Summary", "5_Similar_Schools", "6_ECNU_Profile_EDA", 
        "7_Ranking_Model_Eval"
    ]
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            for df, name in zip(dfs, sheet_names):
                if not df.empty and 'Note' not in df.columns:
                    df.to_excel(writer, sheet_name=name, index=False)
                elif not df.empty and 'Note' in df.columns:
                    df.to_excel(writer, sheet_name=name, index=False)
                    logger.warning(f"工作表 {name} 包含错误占位符，分析失败。")
                else:
                    logger.warning(f"工作表 {name} 的数据为空，跳过导出。")
            
        logger.info(f"所有分析结果已成功导出到: {output_path}")
    except Exception as e:
        logger.error(f"导出Excel失败: {str(e)}", exc_info=True)
        raise


def main():
    """主函数：协调整个数据处理流程"""
    # 使用 output_dir 来构建数据库和最终输出 Excel 路径
    db_path = os.path.join(CONFIG["output_dir"], CONFIG["db_name"]) 
    output_path = os.path.join(CONFIG["output_dir"], CONFIG["output_filename"])
    
    empty_df = pd.DataFrame()
    ecnu_df_basic, china_df, region_df = empty_df, empty_df, empty_df
    cluster_summary, similar_schools_df, ecnu_profile_df, model_summary_df = empty_df, empty_df, empty_df, empty_df

    try:
        # 连接数据库 (文件将创建在 lab6 目录)
        with sqlite3.connect(db_path) as conn:
            init_database(conn)
            # 原始数据仍从 CONFIG["data_dir"] 读取 (lab4\download 目录)
            load_all_csvs(CONFIG["data_dir"], conn)
            
            full_df_with_stats = get_full_df_with_stats(conn)
            if full_df_with_stats.empty:
                logger.error("数据库中没有有效数据，分析终止。")
                return

            ecnu_df_basic, china_df, region_df = perform_analysis(
                full_df_with_stats, CONFIG["target_institution"], CONFIG["target_country"])
            
            try:
                cluster_summary, similar_schools_df = analyze_clustering(full_df_with_stats, CONFIG["target_institution"])
            except Exception as e:
                logger.error(f"聚类分析失败: {e}. 结果将留空。", exc_info=True)
                cluster_summary = pd.DataFrame({'Note': [f"Clustering failed: {e}"]})
                similar_schools_df = pd.DataFrame({'Note': [f"Clustering failed: {e}"]})
                
            try:
                ecnu_profile_df = analyze_ecnu_profile(full_df_with_stats, CONFIG["target_institution"])
            except Exception as e:
                logger.error(f"ECNU画像分析失败: {e}. 结果将留空。", exc_info=True)
                
            # 调用修改后的深度学习排名预测模型 (现已使用随机划分)
            try:
                model_summary_df = build_ranking_model(full_df_with_stats)
            except Exception as e:
                logger.error(f"排名预测建模失败: {e}. 结果将留空。", exc_info=True)
                model_summary_df = pd.DataFrame({'Note': [f"Modeling failed: {e}"]})

        # 6. 导出所有结果 (文件将创建在 lab6 目录)
        export_all_results(output_path, 
                           ecnu_df_basic, china_df, region_df, 
                           cluster_summary, similar_schools_df, 
                           ecnu_profile_df, model_summary_df)

        # 7. 打印关键结果到控制台
        print("\n" + "="*50)
        print(f"--- 分析结果已导出至: {output_path} ---")
        print(f"--- 详细日志文件 (analysis.log) 和数据库文件 (.db) 也在 {CONFIG['output_dir']} ---")
        print("="*50)
        
    except Exception as e:
        logger.critical(f"程序主流程出现严重错误: {e}", exc_info=True)


if __name__ == "__main__":
    if not os.path.isdir(CONFIG["data_dir"]):
        print(f"FATAL ERROR: 数据目录 {CONFIG['data_dir']} 不存在，请检查CONFIG['data_dir']配置。")
    else:
        main()