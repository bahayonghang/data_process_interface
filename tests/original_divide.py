# 顺序取数据集
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 读取数据
df = pd.read_csv('../data_in.csv')  # 这里读取数据

# 假设时间列是 'date'，并将其转换为 datetime 格式
df['DateTime'] = pd.to_datetime(df['DateTime'])

# 1. 按时间排序，确保数据按时间顺序排列
df = df.sort_values(by='DateTime')

# 删除列名为“窑系统单位电耗”范围不在5~50之间的行
df = df[(df['窑系统单位电耗'] >= 5) & (df['窑系统单位电耗'] <= 50)]

# 2. 按照 8:1:1 划分数据集
train_size = int(0.8 * len(df))
val_size = int(0.1 * len(df))
test_size = len(df) - train_size - val_size

# 划分数据集
train_data = df.iloc[:train_size]
val_data = df.iloc[train_size:train_size + val_size]
test_data = df.iloc[train_size + val_size:]

# 输出每个数据集的大小
print(f'Training set size: {len(train_data)}')
print(f'Validation set size: {len(val_data)}')
print(f'Test set size: {len(test_data)}')


# 3. 绘制 KDE 图
def plot_kde(df_train, df_val, df_test, variable):
    plt.figure(figsize=(10, 6))

    # 设置为支持中文的字体，例如 SimHei（黑体）
    rcParams['font.family'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False  # 处理负号的显示问题

    # 为了方便，给每个数据集添加一个数据集标识
    df_train['dataset'] = 'Train'
    df_val['dataset'] = 'Validation'
    df_test['dataset'] = 'Test'

    # 合并三个数据集
    df_combined = pd.concat([df_train[[variable, 'dataset']],
                             df_val[[variable, 'dataset']],
                             df_test[[variable, 'dataset']]])

    # 使用 seaborn 绘制每个数据集的分布，并通过 'dataset' 区分不同数据集
    sns.kdeplot(data=df_combined, x=variable, hue="dataset", common_norm=False, fill=True, palette="tab10")

    # 设置中文字体支持
    rcParams['font.family'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False

    # 不需要手动调用 plt.legend()，seaborn 会自动处理图例
    plt.title(f'{variable} KDE by Dataset')
    plt.xlabel(variable)
    plt.ylabel('Density')

    plt.show()


# 4. 绘制每个变量在不同数据集中的 KDE
for column in train_data.columns:
    if column != 'DateTime':  # 排除日期列
        plot_kde(train_data, val_data, test_data, column)
        