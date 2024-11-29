import pandas as pd
import numpy as np
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from matplotlib import rcParams

# 读取数据
df = pd.read_csv('../data_in.csv')  # 这里读取数据

# 假设时间列是 'DateTime'，并将其转换为 Datetime 格式
df['DateTime'] = pd.to_datetime(df['DateTime'])

# 1. 按时间排序，确保数据按时间顺序排列
df = df.sort_values(by='DateTime')

# 删除列名为“窑系统单位电耗”范围不在5~50之间的行
df = df[(df['窑系统单位电耗'] >= 5) & (df['窑系统单位电耗'] <= 50)]


# 2. 检测时间间隔，自动划分生产周期
def detect_production_periods(df, max_gap=timedelta(hours=2)):
    """
    自动检测生产周期。假设当时间间隔超过 max_gap 时，认为生产周期中断。

    Parameters:
        df (pd.DataFrame): 数据集
        max_gap (timedelta): 最大允许的时间间隔，超出此值则视为生产周期的中断

    Returns:
        pd.DataFrame: 包含生产周期ID的DataFrame
    """
    production_periods = []
    current_period_id = 0

    # 遍历时间戳列
    for i in range(1, len(df)):
        # 计算时间间隔
        time_gap = df['DateTime'].iloc[i] - df['DateTime'].iloc[i - 1]

        # 如果时间间隔大于最大允许间隔，则表示生产周期断开，创建新的生产周期
        if time_gap > max_gap:
            current_period_id += 1

        production_periods.append(current_period_id)

    # 处理第一个数据点，默认属于第一个周期
    production_periods = [0] + production_periods
    df['production_period'] = production_periods
    return df


# 使用检测函数
df = detect_production_periods(df, max_gap=timedelta(hours=1))  # max_gap 可以根据实际情况调整

# 3. 为每个生产周期划分训练集、验证集和测试集
train_data = []
val_data = []
test_data = []

# 按照 8:1:1 划分每个生产周期的数据
for period_id in df['production_period'].unique():
    # 获取当前生产周期的数据
    period_data = df[df['production_period'] == period_id]

    # 按时间顺序分为训练集、验证集和测试集
    n = len(period_data)
    train_size = int(0.8 * n)
    val_size = int(0.1 * n)
    test_size = n - train_size - val_size

    # 划分数据
    train_data.append(period_data.iloc[:train_size])
    val_data.append(period_data.iloc[train_size:train_size + val_size])
    test_data.append(period_data.iloc[train_size + val_size:])

# 4. 合并所有生产周期的数据
train_data = pd.concat(train_data, axis=0)
val_data = pd.concat(val_data, axis=0)
test_data = pd.concat(test_data, axis=0)

# 最终的数据集：train_data, val_data, test_data
print(f'Training set size: {len(train_data)}')
print(f'Validation set size: {len(val_data)}')
print(f'Test set size: {len(test_data)}')


# 1. 统计分析：查看各数据集的描述性统计（均值、标准差、四分位数等）
def summary_statistics(df, dataset_name):
    stats = df.describe().T[['mean', 'std', '25%', '50%', '75%']]
    stats['dataset'] = dataset_name
    return stats


# 分别计算训练集、验证集和测试集的统计信息
train_stats = summary_statistics(train_data, "Train")
val_stats = summary_statistics(val_data, "Validation")
test_stats = summary_statistics(test_data, "Test")

# 合并并输出所有数据集的统计信息
summary_df = pd.concat([train_stats, val_stats, test_stats])
print(summary_df)


# 2. 可视化：使用直方图和核密度估计（KDE）查看每个变量的分布
def plot_distribution(df_train, df_val, df_test, variable):
    plt.figure(figsize=(10, 6))

    # 设置为支持中文的字体，例如 SimHei（黑体）
    rcParams['font.family'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False  # 处理负号的显示问题

    # 为了方便，我们将每个数据集的变量和所属数据集信息合并
    df_train[variable] = df_train[variable]  # 保持原列名
    df_train['dataset'] = 'Train'  # 添加数据集标识

    df_val[variable] = df_val[variable]  # 保持原列名
    df_val['dataset'] = 'Validation'  # 添加数据集标识

    df_test[variable] = df_test[variable]  # 保持原列名
    df_test['dataset'] = 'Test'  # 添加数据集标识

    # 合并三个数据集
    df_combined = pd.concat([df_train[[variable, 'dataset']],
                             df_val[[variable, 'dataset']],
                             df_test[[variable, 'dataset']]])

    # 使用 seaborn 绘制每个数据集的分布，并通过 'dataset' 区分不同数据集
    sns.histplot(df_combined, x=variable, hue="dataset", kde=True, stat='density', bins=30, palette="tab10",
                 multiple="stack")

    # 设置中文字体支持
    rcParams['font.family'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False

    # 不需要手动调用 plt.legend()，seaborn 会自动处理图例
    plt.title(f'{variable} Distribution by Dataset')
    plt.xlabel(variable)
    plt.ylabel('Density')

    plt.show()


# 绘制每个变量在不同数据集中的分布
for column in train_data.columns:
    if column != 'DateTime' and column != 'production_period':  # 排除日期和生产周期列
        rcParams['font.family'] = 'SimHei'  # 你也可以替换成其他安装的 CJK 字体
        rcParams['axes.unicode_minus'] = False  # 处理负号的显示问题
        plot_distribution(train_data, val_data, test_data, column)


# 3. 分布检验：使用 Kolmogorov-Smirnov 检验比较各数据集之间的分布差异
def ks_test(df1, df2, variable):
    stat, p_value = ks_2samp(df1[variable], df2[variable])
    return stat, p_value


# 检查每个变量在训练集、验证集和测试集之间的分布差异
ks_results = []
for column in train_data.columns:
    if column != 'DateTime' and column != 'production_period':  # 排除日期和生产周期列
        ks_train_val = ks_test(train_data, val_data, column)
        ks_train_test = ks_test(train_data, test_data, column)
        ks_val_test = ks_test(val_data, test_data, column)

        ks_results.append({
            "variable": column,
            "train_vs_val_stat": ks_train_val[0], "train_vs_val_p": ks_train_val[1],
            "train_vs_test_stat": ks_train_test[0], "train_vs_test_p": ks_train_test[1],
            "val_vs_test_stat": ks_val_test[0], "val_vs_test_p": ks_val_test[1]
        })

ks_results_df = pd.DataFrame(ks_results)
print(ks_results_df)


# 4. 进一步的可视化：箱线图查看数据的分布
def plot_boxplot(df, dataset_name):
    for column in df.columns:
        if column != 'DateTime' and column != 'production_period':  # 排除日期和生产周期列
            plt.figure(figsize=(10, 6))
            # 设置为支持中文的字体，例如 SimHei（黑体）
            rcParams['font.family'] = 'SimHei'  # 你也可以替换成其他安装的 CJK 字体
            rcParams['axes.unicode_minus'] = False  # 处理负号的显示问题
            sns.boxplot(x='production_period', y=column, data=df)
            plt.title(f'{column} Boxplot by Production Period - {dataset_name}')
            plt.xlabel('Production Period')
            plt.ylabel(column)
            plt.show()


# # 绘制训练集、验证集和测试集的箱线图
# plot_boxplot(train_data, "Train")
# plot_boxplot(val_data, "Validation")
# plot_boxplot(test_data, "Test")

