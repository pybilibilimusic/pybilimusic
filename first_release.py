#!/usr/bin/env python3
"""
PyBiliMusic CLI 首次发布脚本
用于自动化完成代码推送、版本标签创建和GitHub Release发布
"""

import os
import subprocess
import sys
from datetime import datetime


def run_command(cmd, check=True):
    """运行命令并检查结果
    
    Args:
        cmd (str): 要执行的命令
        check (bool): 是否检查命令执行结果
    
    Returns:
        bool: 命令是否成功执行
    """
    print(f"🚀 执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    
    if check and result.returncode != 0:
        print(f"❌ 命令执行失败: {cmd}")
        return False
    
    return result.returncode == 0


def check_environment():
    """检查运行环境是否满足要求
    
    Returns:
        bool: 环境检查是否通过
    """
    print("🔍 检查运行环境...")
    
    # 检查是否在项目根目录
    if not os.path.exists("requirements.txt"):
        print("❌ 请在项目根目录运行此脚本")
        return False
    
    # 检查Git是否可用
    if not run_command("git --version", check=False):
        print("❌ Git 不可用，请先安装Git")
        return False
    
    # 检查GitHub CLI是否可用
    if not run_command("gh --version", check=False):
        print("❌ GitHub CLI 不可用，请先安装GitHub CLI")
        print("   安装命令: winget install GitHub.cli")
        return False
    
    # 检查是否已登录GitHub
    if not run_command("gh auth status", check=False):
        print("❌ 请先登录GitHub CLI")
        print("   登录命令: gh auth login")
        return False
    
    print("✅ 环境检查通过")
    return True


def build_packages():
    """构建分发包
    
    Returns:
        list: 成功构建的文件列表
    """
    print("📦 开始构建分发包...")
    
    # 安装构建工具
    if not run_command("pip install build wheel", check=False):
        print("⚠️  构建工具安装失败，继续尝试构建...")
    
    # 使用现代构建工具
    if run_command("python -m build"):
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
            return []
    else:
        print("❌ 构建失败")
        return []


def git_operations(version):
    """执行Git操作：提交、推送、打标签
    
    Args:
        version (str): 版本号
    
    Returns:
        bool: Git操作是否成功
    """
    print("📤 执行Git操作...")
    
    # 添加所有文件
    if not run_command("git add ."):
        return False
    
    # 提交更改
    commit_msg = f"Release: PyBiliMusic CLI v{version}"
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("⚠️  提交失败，可能没有更改需要提交")
    
    # 推送到GitHub
    if not run_command("git push origin main"):
        print("⚠️  推送失败，尝试设置上游分支...")
        run_command("git branch -M main")
        if not run_command("git push -u origin main"):
            return False
    
    # 创建并推送标签
    tag_msg = f"PyBiliMusic CLI v{version} - First release"
    if not run_command(f'git tag -a v{version} -m "{tag_msg}"'):
        return False
    
    if not run_command(f"git push origin v{version}"):
        return False
    
    print("✅ Git操作完成")
    return True


def create_github_release(version, release_files):
    """创建GitHub Release
    
    Args:
        version (str): 版本号
        release_files (list): 要上传的文件列表
    
    Returns:
        bool: Release创建是否成功
    """
    print("🎊 创建GitHub Release...")
    
    # Release说明
    release_notes = f"""# PyBiliMusic CLI v{version}

🎉 首次发布 - {datetime.now().strftime("%Y-%m-%d")}

## ✨ 功能特性

- **B站视频搜索**: 通过歌曲名搜索B站视频
- **MP4视频下载**: 从B站下载MP4格式视频
- **MP3音频转换**: 使用FFmpeg将视频转换为MP3
- **交互式命令行界面**: 友好的命令行交互体验
- **实时进度显示**: 使用rich库显示下载进度

## 🚀 安装方式

### 从源码安装
```bash
git clone https://github.com/pybilibilimusic/pybilimusic.git
cd pybilimusic
pip install -r requirements.txt
python cli/src/main_CUI.py
```
从分发包安装（如果可用）:
```bash
pip install pybilibilimusic
pybilibilimusic
```

📋 系统要求
Python 3.7+

FFmpeg（用于音频转换）

##⚠️ 注意事项
1.请尊重版权，合理使用本工具

2.所有视频和音乐版权归原作者所有

3.本工具仅限个人使用

##🔄 后续计划

GUI版本正在开发中

更多功能敬请期待
"""
    #构建发布命令
    if release_files:
        files_cmd = " ".join([f'"{f}"' for f in release_files])
        release_cmd = f'gh release create v{version} {files_cmd} --title "PyBiliMusic CLI v{version}" --notes "{release_notes}"'
    else:
        release_cmd = f'gh release create v{version} --title "PyBiliMusic CLI v{version}" --notes "{release_notes}"'
        print("⚠️ 没有构建产物，创建仅包含源码的Release")

    if run_command(release_cmd):
        print("✅ GitHub Release创建成功")
        return True
    else:
        print("❌ GitHub Release创建失败")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🎵 PyBiliMusic CLI 首次发布工具")
    print("=" * 50)
    # 获取版本号
    version = "1.0.0"
    print(f"📝 发布版本: v{version}")

    # 确认发布
    confirm = input("❓ 确认开始发布流程? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 发布取消")
        return

    # 检查环境
    if not check_environment():
        sys.exit(1)

    try:
        # 构建分发包
        release_files = build_packages()
        
        # 执行Git操作
        if not git_operations(version):
            print("❌ Git操作失败")
            sys.exit(1)
        
        # 创建GitHub Release
        if not create_github_release(version, release_files):
            print("❌ GitHub Release创建失败")
            sys.exit(1)
        
        # 发布成功
        print("\n" + "=" * 50)
        print(f"✅ PyBiliMusic CLI v{version} 发布成功!")
        print("🔗 访问: https://github.com/pybilibilimusic/pybilimusic/releases")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n❌ 发布过程被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发布过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
