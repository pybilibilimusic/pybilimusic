import requests
import time
import os
from pathlib import Path
from config import headers
import threading
import queue
import math
from concurrent.futures import ThreadPoolExecutor, as_completed


class DownloadManager:
    """下载管理器，支持断点续传和多线程下载"""

    def __init__(self, url, filename=None, chunk_size=8192, threads=4, resume=False):
        self.url = url
        self.filename = filename or self._get_filename_from_url(url)
        self.chunk_size = chunk_size
        self.threads = threads
        self.resume = resume
        self.temp_dir = Path("./temp")
        self.temp_dir.mkdir(exist_ok=True)
        self.total_size = 0
        self.downloaded = 0
        self.lock = threading.Lock()

    def _get_filename_from_url(self, url):
        """从URL提取文件名"""
        filename = url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = f"download_{int(time.time())}.bin"
        return filename

    def _get_file_size(self):
        """获取文件大小"""
        try:
            head_response = requests.head(self.url, allow_redirects=True, headers=headers)
            head_response.raise_for_status()

            if 'content-length' in head_response.headers:
                return int(head_response.headers['content-length'])

            response = requests.get(self.url, stream=True, allow_redirects=True, headers=headers)
            response.raise_for_status()

            if 'content-length' in response.headers:
                return int(response.headers['content-length'])
        except requests.exceptions.RequestException:
            pass
        return None

    def _get_resume_info(self):
        """获取断点续传信息"""
        if not self.resume:
            return 0, []

        # 检查是否有已下载的部分
        part_files = list(self.temp_dir.glob(f"{self.filename}.part_*"))
        downloaded = 0
        parts = []

        for part_file in part_files:
            try:
                size = part_file.stat().st_size
                downloaded += size
                # 从文件名中提取部分范围信息
                parts.append(str(part_file))
            except:
                pass

        return downloaded, parts

    def _download_part(self, start_byte, end_byte, part_num, progress_callback=None):
        """下载文件的一部分"""
        part_filename = self.temp_dir / f"{self.filename}.part_{part_num}"

        # 如果启用断点续传且文件已存在，获取已下载的大小
        resume_from = 0
        if self.resume and part_filename.exists():
            resume_from = part_filename.stat().st_size
            start_byte += resume_from

        if start_byte > end_byte:
            # 这部分已经下载完成
            return part_filename, True

        headers_copy = headers.copy()
        headers_copy['Range'] = f'bytes={start_byte}-{end_byte}'

        try:
            response = requests.get(self.url, stream=True, headers=headers_copy)
            response.raise_for_status()

            mode = 'ab' if resume_from > 0 else 'wb'
            with open(part_filename, mode) as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        with self.lock:
                            self.downloaded += len(chunk)
                            if progress_callback:
                                progress_callback()

            return part_filename, True

        except Exception as e:
            print(f"\n下载部分 {part_num} 失败: {e}")
            return part_filename, False

    def _merge_parts(self, part_files, final_path):
        """合并所有部分文件"""
        try:
            with open(final_path, 'wb') as final_file:
                for part_file in sorted(part_files,
                                        key=lambda x: int(str(x).split('_')[-1]) if 'part_' in str(x) else 0):
                    with open(part_file, 'rb') as part:
                        while True:
                            chunk = part.read(self.chunk_size)
                            if not chunk:
                                break
                            final_file.write(chunk)
                    # 删除临时文件
                    part_file.unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"合并文件失败: {e}")
            return False

    def download(self):
        """执行下载"""
        # 获取文件大小
        self.total_size = self._get_file_size()
        if not self.total_size:
            print("无法获取文件大小，使用单线程下载")
            return self._single_thread_download()

        print(f"文件大小: {self.total_size:,} 字节 ({self.total_size / 1024 / 1024:.2f} MB)")
        print("-" * 60)

        # 检查断点续传
        resume_downloaded, existing_parts = self._get_resume_info()
        self.downloaded = resume_downloaded

        if resume_downloaded > 0:
            print(f"发现已下载部分: {resume_downloaded:,} 字节 ({resume_downloaded / self.total_size:.1%})")

        # 计算每个线程的下载范围
        part_size = math.ceil(self.total_size / self.threads)
        ranges = []
        for i in range(self.threads):
            start = i * part_size
            end = min((i + 1) * part_size - 1, self.total_size - 1)
            ranges.append((start, end, i))

        # 显示进度条的辅助函数
        start_time = time.time()
        bar_width = 40

        def update_progress():
            nonlocal start_time, bar_width
            elapsed_time = time.time() - start_time

            with self.lock:
                progress = self.downloaded / self.total_size
                filled_length = int(bar_width * progress)
                bar = '█' * filled_length + '-' * (bar_width - filled_length)

                speed = self.downloaded / elapsed_time if elapsed_time > 0 else 0
                if speed > 0 and progress < 1:
                    remaining_time = (self.total_size - self.downloaded) / speed
                    time_str = f"剩余: {remaining_time:.1f}s"
                else:
                    time_str = "剩余: 计算中..."

                print(f'\r[{bar}] {progress:.1%} | '
                      f'{self.downloaded:,}/{self.total_size:,} | '
                      f'{speed / 1024 / 1024:.2f} MB/s | {time_str}',
                      end='', flush=True)

        # 多线程下载
        print(f"使用 {self.threads} 个线程下载...")

        part_files = []
        success = True
        completed = 0

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # 提交所有下载任务
            future_to_part = {
                executor.submit(self._download_part, start, end, part_num, update_progress): part_num
                for start, end, part_num in ranges
            }

            # 处理完成的任务
            for future in as_completed(future_to_part):
                part_num = future_to_part[future]
                try:
                    part_file, part_success = future.result()
                    part_files.append(part_file)
                    completed += 1
                    if not part_success:
                        success = False
                except Exception as e:
                    print(f"\n线程 {part_num} 异常: {e}")
                    success = False

        # 显示最终进度
        update_progress()
        print()

        if success and completed == self.threads:
            # 合并文件
            final_path = Path(self.filename)
            print("正在合并文件...")
            if self._merge_parts(part_files, final_path):
                total_time = time.time() - start_time
                print(f"✓ 下载完成! 总耗时: {total_time:.2f}s, "
                      f"平均速度: {self.downloaded / total_time / 1024 / 1024:.2f} MB/s")
                return True
            else:
                return False
        else:
            print("✗ 下载失败或部分失败")
            return False

    def _single_thread_download(self):
        """单线程下载（作为备选）"""
        # 这里可以调用原始的download函数，或者简单实现
        print("切换到单线程下载模式...")
        return download(self.url, self.filename, self.chunk_size)


def download(url, filename=None, chunk_size=8192, threads=1, resume=False):
    """
    增强版下载函数，支持断点续传和多线程下载

    Args:
        url: 要下载的文件URL
        filename: 保存的文件名（可选，默认为URL中的文件名）
        chunk_size: 下载块大小（字节）
        threads: 下载线程数（默认为1，单线程）
        resume: 是否启用断点续传（默认False）

    Returns:
        bool: 下载是否成功
    """
    # 如果threads=1且resume=False，使用原始下载方式
    if threads == 1 and not resume:
        return _original_download(url, filename, chunk_size)

    # 否则使用增强版下载管理器
    manager = DownloadManager(url, filename, chunk_size, threads, resume)
    return manager.download()


def _original_download(url, filename=None, chunk_size=8192):
    """
    原始下载函数（保持与原代码一致）
    """
    # 这里是你原来的download函数代码，保持原样
    # 为了简洁，我只复制了函数签名，实际使用时需要将原函数内容放在这里

    try:
        # 发送HEAD请求获取文件信息
        head_response = requests.head(url, allow_redirects=True, headers=headers)
        head_response.raise_for_status()

        # 获取文件大小
        if 'content-length' in head_response.headers:
            total_size = int(head_response.headers['content-length'])
        else:
            # 如果HEAD请求没有content-length，尝试GET请求
            response = requests.get(url, stream=True, allow_redirects=True, headers=headers)
            response.raise_for_status()

            if 'content-length' in response.headers:
                total_size = int(response.headers['content-length'])
            else:
                print("无法获取文件大小，将显示简易进度")
                total_size = None
    except requests.exceptions.RequestException as e:
        print(f"获取文件信息失败: {e}")
        return False

    # 确定保存文件名
    if filename is None:
        # 从URL中提取文件名
        filename = url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = f"download_{int(time.time())}.bin"

    if total_size:
        print(f"文件大小: {total_size:,} 字节 ({total_size / 1024 / 1024:.2f} MB)")
    print("-" * 60)

    try:
        # 发送GET请求
        response = requests.get(url, stream=True, allow_redirects=True, headers=headers)
        response.raise_for_status()

        # 如果之前没有获取到文件大小，现在再尝试一次
        if total_size is None and 'content-length' in response.headers:
            total_size = int(response.headers['content-length'])
            print(f"检测到文件大小: {total_size:,} 字节")

        # 进度条参数
        bar_width = 40
        downloaded = 0
        start_time = time.time()
        downloading_path = Path("./temp")
        downloading_name = downloading_path / filename
        # 打开文件进行写入
        with open(downloading_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)

                    # 如果有文件大小信息，显示完整进度条
                    if total_size:
                        progress = downloaded / total_size
                        filled_length = int(bar_width * progress)
                        bar = '█' * filled_length + '-' * (bar_width - filled_length)

                        # 计算下载速度和剩余时间
                        elapsed_time = time.time() - start_time
                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0

                        if speed > 0:
                            remaining_time = (total_size - downloaded) / speed
                            time_str = f"剩余: {remaining_time:.1f}s"
                        else:
                            time_str = "剩余: 计算中..."

                        # 格式化显示
                        print(f'\r[{bar}] {progress:.1%} | '
                              f'{downloaded:,}/{total_size:,} | '
                              f'{speed / 1024 / 1024:.2f} MB/s | {time_str}',
                              end='', flush=True)
                    else:
                        # 没有文件大小信息，只显示已下载量
                        elapsed_time = time.time() - start_time
                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                        print(f'\r已下载: {downloaded:,} 字节 | '
                              f'速度: {speed / 1024 / 1024:.2f} MB/s',
                              end='', flush=True)

        # 下载完成
        total_time = time.time() - start_time
        print()  # 换行

        if total_size:
            if downloaded == total_size:
                print(f"✓ 下载完成! 总耗时: {total_time:.2f}s, "
                      f"平均速度: {downloaded / total_time / 1024 / 1024:.2f} MB/s")
            else:
                print(f"⚠ 下载完成但大小不匹配: 期望 {total_size:,}, 实际 {downloaded:,}")
        else:
            print(f"✓ 下载完成! 总大小: {downloaded:,} 字节, "
                  f"耗时: {total_time:.2f}s")

        return True

    except requests.exceptions.RequestException as e:
        print(f"\n✗ 下载失败: {e}")
        # 删除可能已部分下载的文件
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted incomplete file: {filename}")
        return False
    except KeyboardInterrupt:
        print(f"\n✗ Download was interrupted by the user")
        # 删除可能已部分下载的文件
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted incomplete file: {filename}")
        return False
    except Exception as e:
        print(f"\n✗ 发生未知错误: {e}")
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted incomplete file: {filename}")
        return False


# 如果需要保持完全向后兼容，可以添加这个
original_download = download

# 示例使用方式：
# 1. 原始方式（单线程，无断点续传）：download(url, filename)
# 2. 多线程下载：download(url, filename, threads=4)
# 3. 断点续传：download(url, filename, resume=True)
# 4. 多线程+断点续传：download(url, filename, threads=4, resume=True)