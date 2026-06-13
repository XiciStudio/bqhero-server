#!/usr/bin/env python3
"""数据库初始化脚本 (SQLite).

创建所有表并填充初始数据。
首次启动服务器前运行一次。

用法:
    python init_db.py              # 创建表
    python init_db.py --seed       # 创建表 + 种子数据
    python init_db.py --init-rank  # 初始化排行榜 (rid 800-2500)
    python init_db.py --all        # 全部执行
"""

import sys
import os
import sqlite3

import config

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS `user` (
    `username` TEXT NOT NULL,
    `password` TEXT NOT NULL,
    `uid` TEXT NOT NULL,
    `data` TEXT NOT NULL DEFAULT '[]',
    `Money` INTEGER NOT NULL DEFAULT 5000,
    `TotalRecharge` INTEGER NOT NULL DEFAULT 5000,
    `data_0` TEXT,
    `data_1` TEXT,
    `data_2` TEXT,
    `data_3` TEXT,
    `data_4` TEXT,
    `data_5` TEXT,
    `data_6` TEXT,
    `data_7` TEXT,
    `inunion_id` INTEGER DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `top` (
    `rid` INTEGER NOT NULL,
    `data` TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS `exchange_code` (
    `id` TEXT NOT NULL,
    `num` INTEGER NOT NULL DEFAULT 0,
    `type` TEXT NOT NULL,
    `used` INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `union_data` (
    `id` INTEGER DEFAULT NULL,
    `info` TEXT NOT NULL DEFAULT '{}',
    `application` TEXT NOT NULL DEFAULT '[]',
    `building` TEXT NOT NULL DEFAULT '[]',
    `hegemony` TEXT NOT NULL DEFAULT '[]',
    `member` TEXT NOT NULL DEFAULT '[]'
);
"""


def get_connection() -> sqlite3.Connection:
    db_dir = os.path.dirname(config.DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_tables():
    """创建所有表。"""
    print(f"数据库文件: {config.DB_PATH}")
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()

    # 验证
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for t in tables:
        print(f"  ✓ 表 '{t['name']}' 已就绪")

    conn.close()
    print("\n所有表创建成功。")


def seed_data():
    """插入初始种子数据。"""
    conn = get_connection()

    # 检查 admin 用户是否存在
    cur = conn.execute("SELECT 1 FROM user WHERE username = ?", ("admin",))
    if not cur.fetchone():
        conn.execute(
            "INSERT INTO user (username, password, uid, data, Money, TotalRecharge) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", "pbkdf2:sha256:placeholder", "100001", "[]", 99999, 99999),
        )
        conn.commit()
        print("  ✓ 创建管理员用户 (uid: 100001, 密码: admin123)")
        print("    注意: 首次登录后请修改密码！")

    conn.close()
    print("种子数据插入完成。")


def init_rank_tables():
    """初始化排行榜 (rid 800-2500)。"""
    conn = get_connection()
    print("初始化排行榜 (rid 800-2500)...")
    for rid in range(800, 2501):
        conn.execute(
            "INSERT OR IGNORE INTO top (rid, data) VALUES (?, ?)",
            (rid, "[]"),
        )
        if rid % 200 == 0:
            conn.commit()
            print(f"  进度: rid {rid}...")
    conn.commit()
    conn.close()
    print("排行榜初始化完成。")


def main():
    if len(sys.argv) < 2:
        create_tables()
        print("\n完成。使用 --seed 添加初始数据，--init-rank 初始化排行榜。")
        return

    arg = sys.argv[1]

    if arg == "--seed":
        create_tables()
        seed_data()
    elif arg == "--init-rank":
        init_rank_tables()
    elif arg == "--all":
        create_tables()
        seed_data()
        init_rank_tables()
    else:
        print(f"未知选项: {arg}")
        print("用法: python init_db.py [--seed | --init-rank | --all]")


if __name__ == "__main__":
    main()
