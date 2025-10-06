#!/usr/bin/env python3
"""
PyBiliMusic CLI 首次发布脚本 - 修复标签冲突版
"""

import os
import subprocess
import sys
import time
from datetime import datetime


def run_command_with_retry(cmd, max_retries=3, delay=5, check=True):
    """运行命令并自动重试
    
    Args:
        cmd (str): 要执行的命令
        max_retries (int): 最大重试次数
        delay (int): 重试间隔（秒）
        check (bool): 是否检查命令执行结果
    
    Returns:
        bool: 命令是否成功执行
    """
    for attempt in range(max_retries):
        print(f"🚀 执行 (尝试 {attempt + 1}/{max_retries}): {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # 检查是否需要忽略某些错误
        if result.returncode == 0:
            return True
        
        # 如果是标签已存在的错误，不重试
        if "tag 'v1.0.0' already exists" in result.stderr:
            print("⚠️  标签已存在，跳过创建")
            return True  # 不视为错误
        
        if attempt < max_retries - 1:
            print(f"⚠️  命令执行失败，{delay}秒后重试...")
            time.sleep(delay)
        else:
            if check:
                print(f"❌ 命令执行失败 (尝试了 {max_retries} 次): {cmd}")
                if result.stderr:
                    print(f"   错误: {result.stderr.strip()}")
            return False
    
    return False


def check_existing_tags(version):
    """检查是否已存在标签"""
    print("🔍 检查现有标签...")
    
    result = subprocess.run("git tag -l", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        tags = result.stdout.strip().split('\n')
        if f"v{version}" in tags:
            print(f"⚠️  标签 v{version} 已存在")
            return True
    
    return False


def delete_existing_tag(version):
    """删除已存在的标签"""
    print(f"🗑️  删除现有标签 v{version}...")
    
    # 删除本地标签
    if run_command_with_retry(f"git tag -d v{version}", check=False):
        print("✅ 本地标签已删除")
    
    # 尝试删除远程标签
    if run_command_with_retry(f"git push --delete origin v{version}", check=False):
        print("✅ 远程标签已删除")
    else:
        print("⚠️  远程标签删除失败（可能不存在）")


def check_network_connection():
    """检查网络连接是否正常"""
    print("🔍 检查网络连接...")
    
    # 使用更简单的网络检查方法
    test_commands = [
        "ping -n 1 8.8.8.8",  # 测试基本网络连接
        "git ls-remote --exit-code https://github.com/pybilibilimusic/pybilimusic.git"
    ]
    
    for cmd in test_commands:
        if run_command_with_retry(cmd, max_retries=1, delay=0, check=False):
            print("✅ 网络连接正常")
            return True
    
    print("⚠️  网络连接可能有问题，但继续尝试...")
    return True  # 即使网络检查失败也继续


def setup_git_remote():
    """设置 Git 远程仓库"""
    print("🔧 配置 Git 远程仓库...")
    
    # 检查是否已设置远程仓库
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        # 设置远程仓库
        repo_url = "https://github.com/pybilibilimusic/pybilimusic.git"
        if run_command_with_retry(f"git remote add origin {repo_url}"):
            print(f"✅ 已设置远程仓库: {repo_url}")
            return True
        else:
            print("❌ 设置远程仓库失败")
            return False
    else:
        print(f"✅ 远程仓库已设置: {result.stdout.strip()}")
        return True


def git_operations_with_fallback(version):
    """执行 Git 操作，包含备用方案"""
    print("📤 执行 Git 操作...")
    
    # 添加所有文件
    if not run_command_with_retry("git add ."):
        return False
    
    # 提交更改
    commit_msg = f"Release: PyBiliMusic CLI v{version}"
    if not run_command_with_retry(f'git commit -m "{commit_msg}"', check=False):
        print("⚠️  提交失败，可能没有更改需要提交")
        # 继续执行，可能只是没有新更改
    
    # 推送到 GitHub
    print("🔄 尝试推送到 GitHub...")
    
    push_commands = [
        "git push origin main",     # 标准推送
        "git push -u origin main",  # 设置上游
        "git push"                  # 最简单的方法
    ]
    
    push_success = False
    for cmd in push_commands:
        if run_command_with_retry(cmd, max_retries=2, delay=3):
            push_success = True
            break
    
    if not push_success:
        print("❌ 所有推送方法都失败了")
        print("💡 请手动执行: git push origin main")
        return False
    
    # 检查标签是否已存在
    if check_existing_tags(version):
        # 询问用户是否删除现有标签
        response = input(f"❓ 标签 v{version} 已存在，是否删除并重新创建? (y/N): ").strip().lower()
        if response == 'y':
            delete_existing_tag(version)
        else:
            print("⚠️  跳过标签创建")
            return True
    
    # 创建并推送标签
    tag_msg = f"PyBiliMusic CLI v{version} - First release"
    if not run_command_with_retry(f'git tag -a v{version} -m "{tag_msg}"'):
        return False
    
    if not run_command_with_retry(f"git push origin v{version}"):
        print("⚠️  标签推送失败，但继续发布流程")
        # 继续执行，标签推送失败不是致命错误
    
    print("✅ Git 操作完成")
    return True


def create_github_release_manual_fallback(version, release_files):
    """创建 GitHub Release，包含手动备用方案"""
    print("🎊 创建 GitHub Release...")
    
    # Release 说明
    release_notes = f"""# PyBiliMusic CLI v{version}

🎉 首次发布 - {datetime.now().strftime("%Y-%m-%d")}

## 功能特性
- B站视频搜索
- MP4视频下载  
- MP3音频转换
- 交互式命令行界面

## 安装方式
```bash
git clone https://github.com/pybilibilimusic/pybilimusic.git
cd pybilimusic
pip install -r requirements.txt
python cli/src/main_CUI.py
```
##系统要求
1.Python 3.7+

2.FFmpeg

##注意事项:请尊重版权，合理使用
"""
    if release_files:
        files_cmd = " ".join([f'"{f}"' for f in release_files])
        release_cmd = f'gh release create v{version} {files_cmd} --title "PyBiliMusic CLI v{version}" --notes "{release_notes}"'
    else:
        release_cmd = f'gh release create v{version} --title "PyBiliMusic CLI v{version}" --notes "{release_notes}"'

    if run_command_with_retry(release_cmd, max_retries=2, delay=5):
        print("✅ GitHub Release 创建成功")
        return True
    else:
        print("❌ GitHub CLI 创建 Release 失败")
        print("\n💡 备用方案：请手动创建 Release")
        print("1. 访问: https://github.com/pybilibilimusic/pybilimusic/releases/new")
        print("2. 选择标签: v{}".format(version))
        print("3. 标题: PyBiliMusic CLI v{}".format(version))
        print("4. 描述: 复制上面的发布说明")
    if release_files:
        print("5. 上传文件: {}".format(", ".join(release_files)))
        print("6. 点击 'Publish release'")
          # 询问用户是否已完成手动创建
        response = input("\n❓ 是否已完成手动创建 Release？(y/N): ").strip().lower()
        return response == 'y'    
def build_packages_safe():
    """安全构建分发包，处理可能的错误"""
    print("📦 构建分发包...")
    # 安装构建工具
    run_command_with_retry("pip install build wheel", max_retries=2, delay=3, check=False)

    # 尝试构建
    if run_command_with_retry("python -m build", max_retries=2, delay=3):
        print("✅ 构建成功!")
        
        # 返回构建的文件列表
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            files = [f"dist/{f}" for f in os.listdir(dist_dir) 
                    if f.endswith((".tar.gz", ".whl"))]
            print(f"📁 生成的文件: {files}")
            return files
        else:
            print("❌ dist 目录不存在")
    else:
        print("❌ 构建失败")

    return []
def main():
    """主函数"""
    print("=" * 60)
    print("🎵 PyBiliMusic CLI 首次发布工具 - 修复版")
    print("=" * 60)
    version = "1.0.0"
    print(f"📝 发布版本: v{version}")

    # 检查基本环境
    if not os.path.exists("requirements.txt"):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)

    # 确认发布
    confirm = input("❓ 确认开始发布流程? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 发布取消")
        return

    # 检查网络连接
    if not check_network_connection():
        print("⚠️  网络连接异常，但继续尝试发布流程...")

    try:
        # 设置 Git 远程仓库
        if not setup_git_remote():
            print("❌ Git 远程仓库设置失败")
            sys.exit(1)
        
        # 构建分发包
        release_files = build_packages_safe()
        
        # 执行 Git 操作
        if not git_operations_with_fallback(version):
            print("❌ Git 操作失败")
            print("💡 请手动执行以下命令:")
            print("  git add .")
            print("  git commit -m 'Release: PyBiliMusic CLI v{}'".format(version))
            print("  git push origin main")
            if not check_existing_tags(version):
                print("  git tag -a v{} -m 'PyBiliMusic CLI v{}'".format(version, version))
                print("  git push origin v{}".format(version))
            sys.exit(1)
        
        # 创建 GitHub Release
        if not create_github_release_manual_fallback(version, release_files):
            print("❌ GitHub Release 创建失败")
            print("💡 请手动完成 Release 创建")
            sys.exit(1)
        
        # 发布成功
        print("\n" + "=" * 60)
        print(f"✅ PyBiliMusic CLI v{version} 发布成功!")
        print("🔗 访问: https://github.com/pybilibilimusic/pybilimusic/releases")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ 发布过程被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发布过程中出现错误: {e}")
        print("💡 请根据上面的提示手动完成发布流程")
        sys.exit(1)
if __name__ == "__main__":
    main()
