"""
特征提取模块
分析输入文字的笔画形态、结构布局、书写风格等特征
"""

import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    特征提取器类
    用于从用户输入的文本描述中提取书法字体特征
    """

    def __init__(self):
        """
        初始化特征提取器
        """
        self.stroke_keywords = {
            "楷书": [
                "顿笔", "横平竖直", "方笔", "笔笔分明", "起收笔",
                "粗细变化", "捺脚", "垂露", "悬针", "规整"
            ],
            "行书": [
                "连带", "呼应", "流畅", "自然", "灵动",
                "出锋", "简化", "不拘一格", "自由"
            ],
            "草书": [
                "连笔", "简化", "符号化", "连绵", "一气呵成",
                "合并", "高度简化", "艺术"
            ],
            "隶书": [
                "蚕头燕尾", "波磔", "扁方", "藏锋", "横向舒展",
                "古朴", "厚重", "装饰性"
            ],
            "篆书": [
                "圆润", "对称", "均匀", "流畅", "粗细一致",
                "长方", "纵向", "古朴典雅", "无顿笔"
            ]
        }

        self.structure_keywords = {
            "楷书": ["方正", "严谨", "匀称", "对称", "稳定", "固定"],
            "行书": ["灵活", "错落", "自由", "疏密", "变化"],
            "草书": ["简化", "合并", "符号化", "连绵"],
            "隶书": ["扁方", "横向", "左右舒展", "平稳"],
            "篆书": ["长方", "纵向", "对称", "均匀"]
        }

        self.style_keywords = {
            "楷书": ["端庄", "稳重", "工整", "规范", "严肃"],
            "行书": ["流畅", "实用", "艺术", "灵动"],
            "草书": ["艺术", "奔放", "个性", "辨识度低"],
            "隶书": ["古朴", "庄重", "装饰性", "典雅"],
            "篆书": ["典雅", "古朴", "装饰性", "古老"]
        }

    def extract_features(self, text):
        """
        从用户输入文本中提取特征
        
        参数:
            text: 用户输入的描述文本
            
        返回:
            提取的特征字典
        """
        logger.info(f"开始提取特征，输入文本: {text}")
        
        features = {
            "stroke_features": {},
            "structure_features": {},
            "style_features": {},
            "matched_keywords": [],
            "scores": {}
        }

        for font_name, keywords in self.stroke_keywords.items():
            stroke_score = 0
            for keyword in keywords:
                if keyword in text:
                    stroke_score += 1
                    features["matched_keywords"].append({
                        "font": font_name,
                        "type": "笔画",
                        "keyword": keyword
                    })
            features["stroke_features"][font_name] = stroke_score

        for font_name, keywords in self.structure_keywords.items():
            structure_score = 0
            for keyword in keywords:
                if keyword in text:
                    structure_score += 1
                    features["matched_keywords"].append({
                        "font": font_name,
                        "type": "结构",
                        "keyword": keyword
                    })
            features["structure_features"][font_name] = structure_score

        for font_name, keywords in self.style_keywords.items():
            style_score = 0
            for keyword in keywords:
                if keyword in text:
                    style_score += 1
                    features["matched_keywords"].append({
                        "font": font_name,
                        "type": "风格",
                        "keyword": keyword
                    })
            features["style_features"][font_name] = style_score

        for font_name in ["楷书", "行书", "草书", "隶书", "篆书"]:
            total_score = (
                features["stroke_features"].get(font_name, 0) +
                features["structure_features"].get(font_name, 0) +
                features["style_features"].get(font_name, 0)
            )
            features["scores"][font_name] = total_score

        logger.info(f"特征提取完成，分数: {features['scores']}")
        return features

    def analyze_image_features(self, image_analysis=None):
        """
        分析图像特征（预留接口，当前版本基于文本分析）
        
        参数:
            image_analysis: 图像分析结果
            
        返回:
            图像特征分析结果
        """
        if image_analysis is None:
            image_analysis = {}
        
        features = {
            "stroke_type": image_analysis.get("stroke_type", "未知"),
            "structure_type": image_analysis.get("structure_type", "未知"),
            "writing_style": image_analysis.get("writing_style", "未知")
        }
        
        return features
