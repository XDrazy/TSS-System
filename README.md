# TSS - Ticket Selling System

TSS 是一个基于 Flask 的简单售票系统，旨在模拟公共机器上的售票流程。它支持目的地选择、票务选项配置、支付确认和车票打印功能，适用于演示或小型售票场景。

## 功能特点
- **目的地选择**：从预定义的目的地列表中选择，支持显示价格和库存。
- **票务选项**：支持单程票/多次往返票和普通座/舒适座的选择，动态计算价格。
- **支付确认**：选择支付方式（MCard 或现金）并完成购票。
- **车票打印**：生成带有票号、目的地、类型、座位、价格和时间的车票。
- **库存管理**：每次购票后自动减少对应目的地的票数。
- **多语言支持**：支持中英文切换。
- **简单重置**：通过首页按钮重置购票流程。

## 项目结构
```
TSS系统/
├── main.py                  # 主程序文件
└── templates/               # HTML 模板目录
    ├── base.html            # 基础模板
    ├── index.html           # 首页
    ├── select_destination.html  # 目的地选择页面
    ├── select_options.html  # 票务选项页面
    ├── payment.html         # 支付页面
    └── print_ticket.html    # 车票打印页面
```

## 安装与运行

### 环境要求
- Python 3.6+
- MySQL 5.7+
- pip（Python 包管理器）

### 安装步骤

#### 克隆项目
```bash
git clone <repository-url>
cd TSS系统
```

#### 安装依赖
```bash
pip install flask pymysql
```

#### 配置 MySQL
##### 创建数据库
```sql
CREATE DATABASE tss_db;
```
##### 编辑 `main.py`
将 `your_password` 替换为你的 MySQL root 用户密码：
```python
password="your_password"
```
将 `your_secret_key` 替换为一个随机字符串（用于 Flask session）：
```python
app.secret_key = 'your_secret_key'
```

#### 运行程序
```bash
python main.py
```
程序启动后，访问 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)。

## 首次运行
程序会自动初始化数据库，创建 `destinations` 和 `tickets` 表，并插入初始数据：
- **目的地**：总站 (2U0, ¥10.00, 50 张)、南站 (3K1, ¥8.50, 30 张)、东站 (4M2, ¥12.00, 20 张)。

## 使用说明

### 首页
- 点击“开始购票”进入购票流程，或“重置系统”清除当前会话。

### 选择目的地
- 从下拉菜单选择目的地，显示代码、名称、价格和剩余票数。

### 票务选项
- 选择票种（单程票/多次往返票）和座位类型（普通座/舒适座）。

### 支付
- 查看票务详情，选择支付方式（MCard 或现金），点击“确认支付”。

### 打印车票
- 显示生成的车票信息，包括票号和购票时间。

### 语言切换
- 右上角按钮切换中英文。

## 注意事项
- **库存限制**：当某个目的地的票数为 0 时，无法选择该目的地。
- **错误处理**：如果购票失败（例如数据库问题），会显示提示并返回支付页面。
- **数据库重置**：每次运行程序会清空 `destinations` 表并重置初始数据。
- **安全性**：演示用途，未实现用户认证或高级安全措施。

## 数据库表结构

### `destinations`
| 字段 | 类型 | 描述 |
|------|------|------|
| code | VARCHAR(3) | 目的地代码（主键） |
| name | VARCHAR(50) | 目的地名称 |
| price | DECIMAL(10,2) | 基础价格 |
| stock | INT | 剩余票数 |

### `tickets`
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INT | 自增主键 |
| destination_code | VARCHAR(3) | 目的地代码 |
| ticket_type | VARCHAR(20) | 票种 |
| seat_type | VARCHAR(20) | 座位类型 |
| price | DECIMAL(10,2) | 票价 |
| purchase_time | DATETIME | 购票时间 |
| payment_method | VARCHAR(20) | 支付方式 |
| status | VARCHAR(20) | 票务状态 |

## 开发与调试
- **调试模式**：运行时启用 `debug=True`，便于开发。
- **日志**：初始化和购票失败时会在控制台输出错误信息。
- **扩展**：可添加支付失败模拟、历史记录或其他功能。

## 贡献
欢迎提交问题或改进建议！请通过 GitHub Issues 或 Pull Requests 联系。

## 许可证
本项目仅用于演示，未指定正式许可证。
