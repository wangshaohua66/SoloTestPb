# -*- coding: utf-8 -*-
"""
图像处理模块
使用Pillow库处理上传的书法作品图片，提取图像特征用于字体识别
"""

import logging
import io
import base64

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageStat, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow库未安装，图片识别功能将不可用")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy库未安装，图片分析精度可能降低")


class ImageProcessor:
    """
    图像处理器类
    用于分析书法图片，提取笔画、结构等特征
    """

    def __init__(self):
        """
        初始化图像处理器
        """
        self.allowed_formats = ['JPEG', 'PNG', 'GIF', 'JPG']
        self.max_file_size = 5 * 1024 * 1024
        
        if not PIL_AVAILABLE:
            logger.error("Pillow库未安装，ImageProcessor无法正常工作")

    def validate_image(self, file_storage):
        """
        验证上传的图片
        
        参数:
            file_storage: Flask的FileStorage对象
            
        返回:
            (is_valid, error_message)元组
        """
        if not PIL_AVAILABLE:
            return False, "图片识别功能需要安装Pillow库。请运行: pip3 install Pillow"
        
        try:
            file_storage.seek(0, 2)
            file_size = file_storage.tell()
            file_storage.seek(0)
            
            if file_size > self.max_file_size:
                return False, "文件大小超过限制，最大允许5MB"
            
            img = Image.open(file_storage)
            img.verify()
            file_storage.seek(0)
            
            format_upper = (img.format or '').upper()
            if format_upper not in self.allowed_formats:
                return False, "不支持的图片格式: {}".format(img.format)
            
            return True, None
            
        except Exception as e:
            logger.error("图片验证失败: {}".format(str(e)))
            return False, "图片格式无效: {}".format(str(e))

    def process_image(self, file_storage):
        """
        处理上传的图片并提取特征
        
        参数:
            file_storage: Flask的FileStorage对象
            
        返回:
            图像特征字典
        """
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow库未安装，无法处理图片")
        
        logger.info("开始处理图片")
        
        img = Image.open(file_storage)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        features = {}
        
        features['image_info'] = {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'aspect_ratio': round(img.width / img.height, 3)
        }
        
        features['color_features'] = self._extract_color_features(img)
        features['texture_features'] = self._extract_texture_features(img)
        features['stroke_features'] = self._extract_stroke_features(img)
        features['structure_features'] = self._extract_structure_features(img)
        
        features['font_prediction'] = self._predict_font(features)
        
        logger.info("图片处理完成，预测字体: {}".format(features['font_prediction']))
        return features

    def _extract_color_features(self, img):
        """
        提取颜色特征
        
        参数:
            img: PIL Image对象
            
        返回:
            颜色特征字典
        """
        stat = ImageStat.Stat(img)
        
        r_mean, g_mean, b_mean = stat.mean
        r_std, g_std, b_std = stat.stddev
        
        grayscale = img.convert('L')
        gray_stat = ImageStat.Stat(grayscale)
        gray_mean = gray_stat.mean[0]
        gray_std = gray_stat.stddev[0]
        
        brightness = gray_mean / 255.0
        contrast = gray_std / 255.0
        
        features = {
            'r_mean': round(r_mean, 2),
            'g_mean': round(g_mean, 2),
            'b_mean': round(b_mean, 2),
            'r_std': round(r_std, 2),
            'g_std': round(g_std, 2),
            'b_std': round(b_std, 2),
            'gray_mean': round(gray_mean, 2),
            'gray_std': round(gray_std, 2),
            'brightness': round(brightness, 3),
            'contrast': round(contrast, 3)
        }
        
        return features

    def _extract_texture_features(self, img):
        """
        提取纹理特征
        
        参数:
            img: PIL Image对象
            
        返回:
            纹理特征字典
        """
        grayscale = img.convert('L')
        
        edges = grayscale.filter(ImageFilter.FIND_EDGES)
        edge_stat = ImageStat.Stat(edges)
        edge_intensity = edge_stat.mean[0] / 255.0
        
        if NUMPY_AVAILABLE:
            blur = grayscale.filter(ImageFilter.GaussianBlur(radius=5))
            diff = np.abs(np.array(grayscale) - np.array(blur))
            sharpness = diff.mean() / 255.0
            
            edges_array = np.array(edges)
            edge_density = np.sum(edges_array > 50) / edges_array.size
        else:
            sharpness = 0.08 if edge_intensity > 0.12 else 0.04
            edge_density = edge_intensity * 0.5
        
        features = {
            'edge_intensity': round(edge_intensity, 3),
            'sharpness': round(sharpness, 3),
            'edge_density': round(edge_density, 3)
        }
        
        return features

    def _extract_stroke_features(self, img):
        """
        提取笔画特征
        
        参数:
            img: PIL Image对象
            
        返回:
            笔画特征字典
        """
        grayscale = img.convert('L')
        
        if NUMPY_AVAILABLE:
            img_array = np.array(grayscale)
            
            threshold = np.mean(img_array) * 0.9
            binary = img_array < threshold
            
            white_pixels = np.sum(binary)
            total_pixels = binary.size
            ink_density = white_pixels / total_pixels
            
            horizontal_projection = np.sum(binary, axis=1)
            vertical_projection = np.sum(binary, axis=0)
            
            h_mean = np.mean(horizontal_projection)
            v_mean = np.mean(vertical_projection)
            
            horizontal_variation = np.std(horizontal_projection) / h_mean if h_mean > 0 else 0
            vertical_variation = np.std(vertical_projection) / v_mean if v_mean > 0 else 0
            
            stroke_width = self._estimate_stroke_width(img_array, binary)
        else:
            gray_stat = ImageStat.Stat(grayscale)
            gray_mean = gray_stat.mean[0]
            
            ink_density = (255.0 - gray_mean) / 255.0
            horizontal_variation = 0.2
            vertical_variation = 0.2
            stroke_width = 5.0
        
        features = {
            'ink_density': round(ink_density, 3),
            'horizontal_variation': round(horizontal_variation, 3),
            'vertical_variation': round(vertical_variation, 3),
            'estimated_stroke_width': round(stroke_width, 2),
            'uniformity_score': round(1.0 - min(horizontal_variation, vertical_variation), 3)
        }
        
        return features

    def _estimate_stroke_width(self, img_array, binary):
        """
        估算笔画宽度
        
        参数:
            img_array: 灰度图像数组
            binary: 二值化图像
            
        返回:
            估算的平均笔画宽度
        """
        try:
            from scipy import ndimage
            distance = ndimage.distance_transform_edt(binary)
            max_distances = distance[binary]
            if NUMPY_AVAILABLE and len(max_distances) > 0:
                avg_width = np.mean(max_distances) * 2
                return avg_width
        except ImportError:
            pass
        
        if NUMPY_AVAILABLE:
            stroke_pixels = np.sum(binary)
            total_pixels = binary.size
        else:
            stroke_pixels = 0
            total_pixels = 1
        
        density = stroke_pixels / total_pixels
        
        if density < 0.05:
            return 2.0
        elif density < 0.15:
            return 4.0
        elif density < 0.25:
            return 6.0
        else:
            return 8.0

    def _extract_structure_features(self, img):
        """
        提取结构特征
        
        参数:
            img: PIL Image对象
            
        返回:
            结构特征字典
        """
        aspect_ratio = img.width / img.height
        
        if NUMPY_AVAILABLE:
            grayscale = img.convert('L')
            img_array = np.array(grayscale)
            
            threshold = np.mean(img_array) * 0.9
            binary = img_array < threshold
            
            h, w = binary.shape
            top_half = binary[:h//2, :]
            bottom_half = binary[h//2:, :]
            left_half = binary[:, :w//2]
            right_half = binary[:, w//2:]
            
            top_density = np.sum(top_half) / top_half.size
            bottom_density = np.sum(bottom_half) / bottom_half.size
            left_density = np.sum(left_half) / left_half.size
            right_density = np.sum(right_half) / right_half.size
        else:
            top_density = 0.15
            bottom_density = 0.15
            left_density = 0.15
            right_density = 0.15
        
        vertical_balance = 1.0 - abs(top_density - bottom_density) / max(top_density + bottom_density, 0.01)
        horizontal_balance = 1.0 - abs(left_density - right_density) / max(left_density + right_density, 0.01)
        
        structure_type = self._determine_structure_type(
            aspect_ratio, vertical_balance, horizontal_balance
        )
        
        features = {
            'aspect_ratio': round(aspect_ratio, 3),
            'top_density': round(top_density, 3),
            'bottom_density': round(bottom_density, 3),
            'left_density': round(left_density, 3),
            'right_density': round(right_density, 3),
            'vertical_balance': round(vertical_balance, 3),
            'horizontal_balance': round(horizontal_balance, 3),
            'structure_type': structure_type
        }
        
        return features

    def _determine_structure_type(self, aspect_ratio, vertical_balance, horizontal_balance):
        """
        确定结构类型
        
        参数:
            aspect_ratio: 宽高比
            vertical_balance: 垂直平衡度
            horizontal_balance: 水平平衡度
            
        返回:
            结构类型描述
        """
        if aspect_ratio < 0.7:
            return "纵向长方"
        elif aspect_ratio > 1.3:
            return "横向扁方"
        else:
            if vertical_balance > 0.8 and horizontal_balance > 0.8:
                return "方正对称"
            else:
                return "近方形"

    def _predict_font(self, features):
        """
        基于图像特征预测字体类型
        
        参数:
            features: 图像特征字典
            
        返回:
            预测结果字典，包含各字体的分数
        """
        texture_feat = features['texture_features']
        stroke_feat = features['stroke_features']
        structure_feat = features['structure_features']
        
        scores = {
            '楷书': 0,
            '行书': 0,
            '草书': 0,
            '隶书': 0,
            '篆书': 0
        }
        
        edge_intensity = texture_feat['edge_intensity']
        sharpness = texture_feat['sharpness']
        stroke_width = stroke_feat['estimated_stroke_width']
        ink_density = stroke_feat['ink_density']
        uniformity = stroke_feat['uniformity_score']
        aspect_ratio = structure_feat['aspect_ratio']
        v_balance = structure_feat['vertical_balance']
        h_balance = structure_feat['horizontal_balance']
        
        if uniformity > 0.5:
            scores['楷书'] += 3
            scores['篆书'] += 3
            scores['隶书'] += 2
        if uniformity < 0.3:
            scores['草书'] += 3
            scores['行书'] += 2
        
        if stroke_width < 4:
            scores['草书'] += 2
            scores['行书'] += 1
        elif stroke_width > 7:
            scores['隶书'] += 2
            scores['篆书'] += 2
        
        if edge_intensity > 0.15:
            scores['楷书'] += 2
            scores['篆书'] += 2
        if edge_intensity < 0.1:
            scores['草书'] += 2
            scores['行书'] += 1
        
        if aspect_ratio < 0.7:
            scores['篆书'] += 3
        elif aspect_ratio > 1.3:
            scores['隶书'] += 3
        else:
            scores['楷书'] += 2
            scores['行书'] += 1
        
        if v_balance > 0.8 and h_balance > 0.8:
            scores['篆书'] += 2
            scores['楷书'] += 1
        
        if sharpness > 0.1:
            scores['楷书'] += 2
        if sharpness < 0.05:
            scores['草书'] += 2
        
        if ink_density < 0.1:
            scores['行书'] += 1
        elif ink_density > 0.2:
            scores['隶书'] += 1
            scores['篆书'] += 1
        
        total_score = sum(scores.values())
        if total_score > 0:
            probabilities = {font: score / total_score for font, score in scores.items()}
        else:
            probabilities = {font: 0.2 for font in scores.keys()}
        
        return {
            'scores': scores,
            'probabilities': probabilities
        }

    def generate_description(self, features):
        """
        根据图像特征生成文字描述
        
        参数:
            features: 图像特征字典
            
        返回:
            文字描述字符串
        """
        desc_parts = []
        
        stroke_feat = features['stroke_features']
        structure_feat = features['structure_features']
        texture_feat = features['texture_features']
        
        if stroke_feat['uniformity_score'] > 0.5:
            desc_parts.append("笔画规整")
        else:
            desc_parts.append("笔画灵动")
        
        if stroke_feat['estimated_stroke_width'] > 6:
            desc_parts.append("笔画粗壮")
        elif stroke_feat['estimated_stroke_width'] < 4:
            desc_parts.append("笔画纤细")
        
        if structure_feat['structure_type'] == "纵向长方":
            desc_parts.append("结构纵向长方")
        elif structure_feat['structure_type'] == "横向扁方":
            desc_parts.append("结构扁方横向舒展")
        elif structure_feat['structure_type'] == "方正对称":
            desc_parts.append("结构方正对称")
        
        if texture_feat['edge_intensity'] > 0.15:
            desc_parts.append("笔画清晰分明")
        else:
            desc_parts.append("笔画有连带")
        
        if structure_feat['vertical_balance'] > 0.7 and structure_feat['horizontal_balance'] > 0.7:
            desc_parts.append("结构均匀对称")
        
        return "，".join(desc_parts) + "。"

    def image_to_base64(self, file_storage):
        """
        将图片转换为Base64编码
        
        参数:
            file_storage: Flask的FileStorage对象
            
        返回:
            Base64编码字符串
        """
        file_storage.seek(0)
        img_data = file_storage.read()
        base64_encoded = base64.b64encode(img_data).decode('utf-8')
        return base64_encoded
