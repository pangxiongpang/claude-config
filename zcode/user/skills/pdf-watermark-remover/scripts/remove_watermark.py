#!/usr/bin/env python3
"""
PDF Watermark Remover - 从PDF文件中去除水印

This script analyzes PDF structure, detects overlay images that serve as
watermarks, and deletes them while preserving page content.

Example:
    $ python remove_watermark.py input.pdf output.pdf
    $ python remove_watermark.py --detect-only input.pdf
    $ python remove_watermark.py --batch *.pdf
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    print('{"error": "PyMuPDF not installed. Run: pip install PyMuPDF", "error_type": "dependency"}', file=sys.stderr)
    sys.exit(1)


class PDFWatermarkRemover:
    """
    PDF Watermark Remover - 分析PDF结构并删除水印图片

    Attributes:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        watermark_threshold_width: 水印图片最大宽度阈值
        watermark_threshold_height: 水印图片最大高度阈值
        watermark_position_x: 水印位置X阈值
        watermark_position_y: 水印位置Y阈值

    Example:
        >>> remover = PDFWatermarkRemover("input.pdf", "output.pdf")
        >>> result = remover.process()
        >>> print(result)
    """

    def __init__(self, input_path: str, output_path: Optional[str] = None,
                 watermark_threshold_width: int = 300,
                 watermark_threshold_height: int = 100,
                 watermark_position_x: float = 400.0,
                 watermark_position_y: float = 700.0):
        """
        Initialize PDFWatermarkRemover.

        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径，如果为None则自动生成
            watermark_threshold_width: 水印图片最大宽度阈值（像素）
            watermark_threshold_height: 水印图片最大高度阈值（像素）
            watermark_position_x: 水印位置X阈值（PDF点）
            watermark_position_y: 水印位置Y阈值（PDF点）

        Raises:
            ValueError: If input_path is empty
            FileNotFoundError: If input file does not exist
        """
        if not input_path:
            raise ValueError("input_path cannot be empty")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        self.input_path = input_path
        self.output_path = output_path or self._generate_output_path(input_path)
        self.watermark_threshold_width = watermark_threshold_width
        self.watermark_threshold_height = watermark_threshold_height
        self.watermark_position_x = watermark_position_x
        self.watermark_position_y = watermark_position_y

    def _generate_output_path(self, input_path: str) -> str:
        """
        Generate output file path with "_clean" suffix.

        Args:
            input_path: 输入文件路径

        Returns:
            输出文件路径
        """
        path = Path(input_path)
        return str(path.parent / f"{path.stem}_clean{path.suffix}")

    def _is_watermark(self, img_info: Dict, page_rect: Tuple[float, float, float, float]) -> bool:
        """
        判断图片是否为水印

        Args:
            img_info: 图片信息字典
            page_rect: 页面矩形 (x0, y0, x1, y1)

        Returns:
            True if image is likely a watermark, False otherwise
        """
        # 获取图片尺寸
        img_width = img_info.get('width', 0)
        img_height = img_info.get('height', 0)

        # 获取图片位置
        x0 = img_info.get('x0', 0)
        y0 = img_info.get('y0', 0)

        # 检查尺寸是否符合水印特征
        if img_width > self.watermark_threshold_width or img_height > self.watermark_threshold_height:
            return False

        # 检查位置是否在右下角
        if x0 < self.watermark_position_x or y0 < self.watermark_position_y:
            return False

        return True

    def analyze_page(self, page: fitz.Page) -> List[Dict]:
        """
        分析单页PDF，查找水印图片

        Args:
            page: PyMuPDF页面对象

        Returns:
            水印图片信息列表
        """
        watermarks = []

        # 获取页面中的图片
        image_list = page.get_images(full=True)

        # 获取页面尺寸
        page_rect = page.rect

        for img in image_list:
            xref = img[0]

            # 获取图片位置
            img_rects = page.get_image_rects(xref)
            if not img_rects:
                continue

            rect = img_rects[0]

            # 获取图片基本信息
            base_image = page.parent.extract_image(xref)
            img_width = base_image['width']
            img_height = base_image['height']

            # 构建图片信息字典
            img_info = {
                'xref': xref,
                'width': img_width,
                'height': img_height,
                'x0': rect.x0,
                'y0': rect.y0,
                'x1': rect.x1,
                'y1': rect.y1,
                'ext': base_image['ext']
            }

            # 判断是否为水印
            if self._is_watermark(img_info, page_rect):
                watermarks.append(img_info)

        return watermarks

    def remove_watermarks_from_page(self, page: fitz.Page) -> int:
        """
        从单页PDF中删除水印图片

        Args:
            page: PyMuPDF页面对象

        Returns:
            删除的水印数量
        """
        # 分析页面查找水印
        watermarks = self.analyze_page(page)

        # 删除每个水印
        for wm in watermarks:
            try:
                page.delete_image(wm['xref'])
            except Exception as e:
                print(f"Warning: Failed to delete watermark on page: {e}", file=sys.stderr)

        return len(watermarks)

    def process(self) -> Dict:
        """
        处理PDF文件，删除所有水印

        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'input_file': self.input_path,
            'output_file': self.output_path,
            'pages_processed': 0,
            'watermarks_removed': 0,
            'details': []
        }

        try:
            # 打开PDF文件
            doc = fitz.open(self.input_path)

            # 处理每一页
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # 分析页面
                watermarks = self.analyze_page(page)

                # 删除水印
                removed_count = self.remove_watermarks_from_page(page)

                # 记录详情
                page_detail = {
                    'page': page_num + 1,
                    'watermark_found': len(watermarks) > 0,
                    'watermarks_count': len(watermarks),
                    'action': 'deleted' if removed_count > 0 else 'none'
                }

                if watermarks:
                    page_detail['watermark_position'] = {
                        'x': watermarks[0].get('x0', 0),
                        'y': watermarks[0].get('y0', 0)
                    }
                    page_detail['watermark_size'] = {
                        'width': watermarks[0].get('width', 0),
                        'height': watermarks[0].get('height', 0)
                    }

                result['details'].append(page_detail)
                result['watermarks_removed'] += removed_count
                result['pages_processed'] += 1

            # 保存修改后的PDF
            doc.save(self.output_path)
            doc.close()

            result['success'] = True

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['error_type'] = 'runtime'

        return result

    def detect_only(self) -> Dict:
        """
        仅检测水印，不删除

        Returns:
            检测结果字典
        """
        result = {
            'success': False,
            'input_file': self.input_path,
            'watermarks_found': 0,
            'details': []
        }

        try:
            # 打开PDF文件
            doc = fitz.open(self.input_path)

            # 处理每一页
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # 分析页面
                watermarks = self.analyze_page(page)

                # 记录详情
                page_detail = {
                    'page': page_num + 1,
                    'watermark_found': len(watermarks) > 0,
                    'watermarks_count': len(watermarks)
                }

                if watermarks:
                    page_detail['watermark_position'] = {
                        'x': watermarks[0].get('x0', 0),
                        'y': watermarks[0].get('y0', 0)
                    }
                    page_detail['watermark_size'] = {
                        'width': watermarks[0].get('width', 0),
                        'height': watermarks[0].get('height', 0)
                    }

                result['details'].append(page_detail)
                result['watermarks_found'] += len(watermarks)

            doc.close()
            result['success'] = True

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['error_type'] = 'runtime'

        return result


def check_prerequisites() -> Dict:
    """
    检查系统先决条件

    Returns:
        检查结果字典
    """
    checks = []

    # 检查Python版本
    python_version = sys.version_info
    checks.append({
        'check': 'Python version',
        'required': '3.7+',
        'found': f'{python_version.major}.{python_version.minor}.{python_version.micro}',
        'ok': python_version >= (3, 7)
    })

    # 检查PyMuPDF
    try:
        import fitz
        checks.append({
            'check': 'PyMuPDF',
            'required': 'Installed',
            'found': 'Installed',
            'ok': True
        })
    except ImportError:
        checks.append({
            'check': 'PyMuPDF',
            'required': 'Installed',
            'found': 'Not installed',
            'ok': False
        })

    all_ok = all(check['ok'] for check in checks)

    return {
        'ready': all_ok,
        'checks': checks
    }


def get_diagnostics() -> Dict:
    """
    获取skill诊断信息

    Returns:
        诊断信息字典
    """
    return {
        'skill': 'pdf-watermark-remover',
        'version': '1.0.0',
        'harness_level': '5',
        'commands': ['remove', 'detect', 'check-prereqs', 'diagnostics'],
        'harness_features': {
            'input_validation': True,
            'output_sanity': True,
            'error_handling': True
        }
    }


def main():
    """Main function with argparse."""
    parser = argparse.ArgumentParser(
        description='PDF Watermark Remover - Remove watermarks from PDF files'
    )

    # 主要参数
    parser.add_argument('input', nargs='?', help='Input PDF file path')
    parser.add_argument('output', nargs='?', help='Output PDF file path')

    # 模式参数
    parser.add_argument('--detect-only', action='store_true',
                       help='Only detect watermarks, do not remove')
    parser.add_argument('--batch', action='store_true',
                       help='Batch process multiple files')

    # 水印检测参数
    parser.add_argument('--max-width', type=int, default=300,
                       help='Maximum watermark width (default: 300)')
    parser.add_argument('--max-height', type=int, default=100,
                       help='Maximum watermark height (default: 100)')
    parser.add_argument('--min-x', type=float, default=400.0,
                       help='Minimum X position for watermark (default: 400.0)')
    parser.add_argument('--min-y', type=float, default=700.0,
                       help='Minimum Y position for watermark (default: 700.0)')

    # 系统命令
    parser.add_argument('--check-prereqs', action='store_true',
                       help='Check system prerequisites')
    parser.add_argument('--diagnostics', action='store_true',
                       help='Show skill diagnostics')

    args = parser.parse_args()

    # 处理系统命令
    if args.check_prereqs:
        result = check_prerequisites()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['ready'] else 1)

    if args.diagnostics:
        result = get_diagnostics()
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # 验证输入
    if not args.input:
        parser.error('Input file is required (unless using --check-prereqs or --diagnostics)')

    # 批量处理模式
    if args.batch:
        input_files = [args.input]
        if args.output:
            input_files.extend(args.output.split())

        results = []
        for input_file in input_files:
            if not os.path.exists(input_file):
                results.append({
                    'success': False,
                    'input_file': input_file,
                    'error': f'File not found: {input_file}',
                    'error_type': 'validation'
                })
                continue

            remover = PDFWatermarkRemover(
                input_file,
                watermark_threshold_width=args.max_width,
                watermark_threshold_height=args.max_height,
                watermark_position_x=args.min_x,
                watermark_position_y=args.min_y
            )

            if args.detect_only:
                result = remover.detect_only()
            else:
                result = remover.process()

            results.append(result)

        print(json.dumps({'results': results}, indent=2))
        sys.exit(0)

    # 单文件处理模式
    try:
        remover = PDFWatermarkRemover(
            args.input,
            args.output,
            watermark_threshold_width=args.max_width,
            watermark_threshold_height=args.max_height,
            watermark_position_x=args.min_x,
            watermark_position_y=args.min_y
        )

        if args.detect_only:
            result = remover.detect_only()
        else:
            result = remover.process()

        print(json.dumps(result, indent=2))

        if result['success']:
            sys.exit(0)
        else:
            sys.exit(1)

    except ValueError as e:
        error_result = {
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError as e:
        error_result = {
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'error_type': 'runtime'
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()