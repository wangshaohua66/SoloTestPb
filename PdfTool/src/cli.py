import click
from .pdf_merger import PDFMerger
from .pdf_splitter import PDFSplitter
from .pdf_text_extractor import PDFTextExtractor
from .pdf_image_extractor import PDFImageExtractor
from .pdf_header_footer import PDFHeaderFooter
from .pdf_security import PDFSecurity


@click.group()
def cli():
    """
    PDF文档处理工具 - 支持合并、拆分、提取文本和图片等操作
    """
    pass


@cli.command()
@click.option('--inputs', '-i', multiple=True, required=True, help='输入PDF文件路径（可多次指定）')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
def merge(inputs, output):
    """合并多个PDF文件"""
    merger = PDFMerger()
    merger.merge_pdfs(list(inputs), output)
    click.echo(f'合并完成，输出文件：{output}')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
@click.option('--start', '-s', type=int, default=1, help='起始页码')
@click.option('--end', '-e', type=int, required=True, help='结束页码')
def split(input, output, start, end):
    """按页码范围拆分PDF"""
    splitter = PDFSplitter()
    splitter.split_by_range(input, output, start, end)
    click.echo(f'拆分完成，输出文件：{output}')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', help='输出TXT文件路径（可选）')
@click.option('--start', '-s', type=int, help='起始页码（可选）')
@click.option('--end', '-e', type=int, help='结束页码（可选）')
def extract_text(input, output, start, end):
    """从PDF提取文本"""
    extractor = PDFTextExtractor()
    text = extractor.extract_text(input, output, start, end)
    if output:
        click.echo(f'文本提取完成，输出文件：{output}')
    else:
        click.echo(text)


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output-dir', '-o', required=True, help='输出图片目录')
@click.option('--start', '-s', type=int, help='起始页码（可选）')
@click.option('--end', '-e', type=int, help='结束页码（可选）')
@click.option('--convert', '-c', is_flag=True, help='将页面转换为图片而不是提取内嵌图片')
@click.option('--dpi', type=int, default=200, help='转换分辨率（默认200）')
def extract_images(input, output_dir, start, end, convert, dpi):
    """从PDF提取图片"""
    extractor = PDFImageExtractor()
    if convert:
        files = extractor.convert_to_images(input, output_dir, start, end, dpi)
    else:
        files = extractor.extract_images(input, output_dir, start, end)
    click.echo(f'图片提取完成，共提取{len(files)}张图片')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
@click.option('--position', '-p', default='bottom_right', help='页码位置')
@click.option('--font-size', '-f', type=int, default=12, help='字体大小')
@click.option('--start-num', '-n', type=int, default=1, help='起始页码')
def add_page_numbers(input, output, position, font_size, start_num):
    """给PDF添加页码"""
    processor = PDFHeaderFooter()
    processor.add_page_numbers(input, output, position, font_size, start_num)
    click.echo(f'页码添加完成，输出文件：{output}')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
@click.option('--header', '-h', default='', help='页眉文本')
@click.option('--footer', '-f', default='', help='页脚文本')
@click.option('--font-size', '-s', type=int, default=10, help='字体大小')
def add_header_footer(input, output, header, footer, font_size):
    """给PDF添加页眉页脚"""
    processor = PDFHeaderFooter()
    processor.add_header_footer(input, output, header, footer, font_size)
    click.echo(f'页眉页脚添加完成，输出文件：{output}')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
@click.option('--password', '-p', required=True, help='加密密码')
def encrypt(input, output, password):
    """加密PDF文件"""
    security = PDFSecurity()
    security.encrypt_pdf(input, output, password)
    click.echo(f'加密完成，输出文件：{output}')


@cli.command()
@click.option('--input', '-i', required=True, help='输入PDF文件路径')
@click.option('--output', '-o', required=True, help='输出PDF文件路径')
@click.option('--password', '-p', required=True, help='解密密码')
def decrypt(input, output, password):
    """解密PDF文件"""
    security = PDFSecurity()
    security.decrypt_pdf(input, output, password)
    click.echo(f'解密完成，输出文件：{output}')


if __name__ == '__main__':
    cli()
