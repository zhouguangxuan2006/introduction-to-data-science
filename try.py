import os
import pandas as pd
import sqlite3
import logging
from typing import Optional

# 配置参数集中管理
CONFIG = {
    "data_dir": r"D:\vsc\数据科学与大数据技术导论\download\download",
    "db_name": "university_ranking.db",
    "output_filename": "analysis_results.xlsx",
    "target_institution": "EAST CHINA NORMAL UNIVERSITY",
    "target_country": "CHINA MAINLAND",
    "csv_encodings": ["utf-8", "gbk", "latin1"],
    "required_columns": 7  # 原始CSV至少需要的列数
}

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler(os.path.join(CONFIG["data_dir"], "analysis.log"))  # 输出到日志文件
    ]
)
logger = logging.getLogger(__name__)


def init_database(conn: sqlite3.Connection) -> None:
    """初始化数据库表结构"""
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS rankings")
        cursor.execute("""
        CREATE TABLE rankings (
            subject TEXT,
            rank INTEGER,
            institution TEXT,
            country TEXT,
            documents INTEGER,
            cites INTEGER,
            cites_per_paper REAL,
            top_papers INTEGER
        )
        """)
        conn.commit()
        logger.info("数据库表结构初始化完成")
    except sqlite3.Error as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise  # 抛出异常终止程序


def clean_and_load_csv(file_path: str, subject: str, conn: sqlite3.Connection) -> None:
    """清洗并加载单个CSV文件到数据库"""
    df: Optional[pd.DataFrame] = None
    
    # 尝试多种编码读取CSV
    for enc in CONFIG["csv_encodings"]:
        try:
            df = pd.read_csv(file_path, encoding=enc, skiprows=1)
            logger.debug(f"使用编码 {enc} 成功读取 {file_path}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.warning(f"读取 {file_path} 时发生错误: {str(e)}")
            return

    # 数据有效性校验
    if df is None:
        logger.warning(f"无法读取文件 (所有编码尝试失败): {file_path}")
        return
    if df.shape[1] < CONFIG["required_columns"]:
        logger.warning(f"文件列数不足 {CONFIG['required_columns']}: {file_path} (实际: {df.shape[1]})")
        return

    try:
        # 数据清洗
        df.columns = [str(c).strip() for c in df.columns]  # 去除列名空格
        df = df.dropna(how="all")  # 删除全空行
        
        # 重命名列（基于位置映射）
        df = df.rename(columns={
            df.columns[0]: "rank",
            df.columns[1]: "institution",
            df.columns[2]: "country",
            df.columns[3]: "documents",
            df.columns[4]: "cites",
            df.columns[5]: "cites_per_paper",
            df.columns[-1]: "top_papers"
        })
        
        # 类型转换与异常值处理
        numeric_cols = ["rank", "documents", "cites", "top_papers"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df["cites_per_paper"] = pd.to_numeric(df["cites_per_paper"], errors="coerce")
        
        # 去除关键列缺失值
        df = df.dropna(subset=["rank", "institution", "country"])
        
        # 添加学科列并调整顺序
        df["subject"] = subject
        df = df[["subject", "rank", "institution", "country", 
                "documents", "cites", "cites_per_paper", "top_papers"]]
        
        # 写入数据库
        df.to_sql("rankings", conn, if_exists="append", index=False)
        logger.info(f"导入成功: {subject} ({len(df)} 行数据)")
        
    except Exception as e:
        logger.error(f"处理 {file_path} 时失败: {str(e)}")


def load_all_csvs(data_dir: str, conn: sqlite3.Connection) -> None:
    """批量加载目录下所有CSV文件"""
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    if not csv_files:
        logger.warning(f"在 {data_dir} 未找到任何CSV文件")
        return
        
    logger.info(f"发现 {len(csv_files)} 个CSV文件，开始批量导入...")
    for file in csv_files:
        subject = file.replace(".csv", "")
        file_path = os.path.join(data_dir, file)
        clean_and_load_csv(file_path, subject, conn)


def perform_analysis(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """执行数据分析并返回结果"""
    # 1. 华东师范大学表现分析
    sql_ecnu = f"""
    SELECT subject, rank, cites_per_paper, documents, top_papers
    FROM rankings
    WHERE institution LIKE '%{CONFIG['target_institution']}%'
    ORDER BY rank;
    """
    ecnu_df = pd.read_sql_query(sql_ecnu, conn)
    logger.info(f"华东师范大学分析完成 (找到 {len(ecnu_df)} 条记录)")

    # 2. 中国大陆高校表现分析
    sql_china = f"""
    SELECT subject,
           COUNT(*) AS num_institutions,
           AVG(rank) AS avg_rank,
           SUM(CASE WHEN rank <= 10 THEN 1 ELSE 0 END) AS top10,
           SUM(CASE WHEN rank <= 100 THEN 1 ELSE 0 END) AS top100
    FROM rankings
    WHERE country LIKE '%{CONFIG['target_country']}%'
    GROUP BY subject;
    """
    china_df = pd.read_sql_query(sql_china, conn)
    logger.info(f"中国大陆高校分析完成 (涵盖 {len(china_df)} 个学科)")

    # 3. 全球各地区表现分析
    sql_region = """
    SELECT subject,
           country,
           COUNT(*) AS num_institutions,
           AVG(rank) AS avg_rank
    FROM rankings
    GROUP BY subject, country
    ORDER BY subject, avg_rank;
    """
    region_df = pd.read_sql_query(sql_region, conn)
    logger.info(f"全球地区分析完成 (找到 {len(region_df)} 条地区-学科记录)")

    return ecnu_df, china_df, region_df


def export_results(ecnu_df: pd.DataFrame, china_df: pd.DataFrame, region_df: pd.DataFrame, output_path: str) -> None:
    """导出分析结果到Excel"""
    try:
        with pd.ExcelWriter(output_path) as writer:
            ecnu_df.to_excel(writer, sheet_name="ECNU", index=False)
            china_df.to_excel(writer, sheet_name="China", index=False)
            region_df.to_excel(writer, sheet_name="Regions", index=False)
        logger.info(f"分析结果已成功导出到: {output_path}")
    except Exception as e:
        logger.error(f"导出Excel失败: {str(e)}")
        raise


def main():
    """主函数：协调整个数据处理流程"""
    try:
        # 初始化路径
        db_path = os.path.join(CONFIG["data_dir"], CONFIG["db_name"])
        output_path = os.path.join(CONFIG["data_dir"], CONFIG["output_filename"])
        
        # 数据库操作主流程
        with sqlite3.connect(db_path) as conn:
            init_database(conn)
            load_all_csvs(CONFIG["data_dir"], conn)
            ecnu_df, china_df, region_df = perform_analysis(conn)
        
        # 导出结果（数据库连接已关闭，使用内存中的DataFrame）
        export_results(ecnu_df, china_df, region_df, output_path)
        
        # 打印关键结果到控制台
        print("\n===== 华东师范大学(ECNU) 各学科表现 =====")
        print(ecnu_df if not ecnu_df.empty else "未找到记录")
        
        print("\n===== 中国大陆高校总体表现 (前10学科) =====")
        print(china_df.head(10))
        
        print("\n===== 全球地区表现 (前5行示例) =====")
        print(region_df.head(5))
        
        print(f"\n✅ 分析完成，结果已保存至: {output_path}")

    except Exception as e:
        logger.critical(f"程序执行失败: {str(e)}", exc_info=True)
        print(f"错误: {str(e)}，详情请查看日志文件")


if __name__ == "__main__":
    main()