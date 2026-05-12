"""
字体识别器模块
根据提取的特征匹配字体库，输出最可能的字体类型及置信度
"""

import logging
from app.font_library import FONT_LIBRARY, get_font

logger = logging.getLogger(__name__)


class FontRecognizer:
    """
    字体识别器类
    基于特征匹配算法进行书法字体识别
    """

    def __init__(self):
        """
        初始化字体识别器
        """
        self.font_weights = {
            "楷书": 1.0,
            "行书": 1.0,
            "草书": 1.0,
            "隶书": 1.0,
            "篆书": 1.0
        }

    def recognize(self, features, input_text=""):
        """
        识别书法字体
        
        参数:
            features: 提取的特征字典
            input_text: 用户输入的原始文本
            
        返回:
            识别结果字典
        """
        logger.info("开始字体识别")

        scores = features.get("scores", {})
        total_score = sum(scores.values())

        if total_score == 0:
            base_confidence = 0.15
            results = []
            for font_name in ["楷书", "行书", "草书", "隶书", "篆书"]:
                results.append({
                    "font_name": font_name,
                    "confidence": base_confidence,
                    "score": 0
                })
            
            return {
                "primary_result": self._build_result("楷书", 0.15, features, input_text),
                "all_results": results,
                "similar_fonts": []
            }

        results = []
        for font_name, score in scores.items():
            confidence = score / total_score if total_score > 0 else 0
            results.append({
                "font_name": font_name,
                "confidence": confidence,
                "score": score
            })

        results.sort(key=lambda x: x["confidence"], reverse=True)

        primary_font = results[0]["font_name"]
        primary_confidence = results[0]["confidence"]

        primary_result = self._build_result(
            primary_font, primary_confidence, features, input_text
        )

        similar_fonts = self._find_similar_fonts(primary_font, results)

        return {
            "primary_result": primary_result,
            "all_results": results,
            "similar_fonts": similar_fonts
        }

    def _build_result(self, font_name, confidence, features, input_text):
        """
        构建识别结果
        
        参数:
            font_name: 字体名称
            confidence: 置信度
            features: 提取的特征
            input_text: 原始输入文本
            
        返回:
            构建完成的结果字典
        """
        font_info = get_font(font_name)
        
        result = {
            "font_name": font_name,
            "confidence": round(confidence * 100, 2),
            "font_info": font_info,
            "matched_keywords": self._get_matched_keywords(font_name, features),
            "analysis": self._generate_analysis(font_name, confidence, features, input_text)
        }
        
        return result

    def _get_matched_keywords(self, font_name, features):
        """
        获取指定字体的匹配关键词
        
        参数:
            font_name: 字体名称
            features: 特征字典
            
        返回:
            匹配的关键词列表
        """
        matched = features.get("matched_keywords", [])
        font_keywords = [k for k in matched if k["font"] == font_name]
        return font_keywords

    def _generate_analysis(self, font_name, confidence, features, input_text):
        """
        生成识别分析说明
        
        参数:
            font_name: 识别出的字体名称
            confidence: 置信度
            features: 特征字典
            input_text: 原始输入文本
            
        返回:
            分析说明字符串
        """
        font_info = get_font(font_name)
        
        analysis_parts = []
        analysis_parts.append(f"根据您的描述，该书法作品最可能是{font_name}。")
        
        matched_keywords = self._get_matched_keywords(font_name, features)
        if matched_keywords:
            keywords = [k["keyword"] for k in matched_keywords]
            analysis_parts.append(f"匹配到的特征关键词包括：{'、'.join(keywords)}。")
        
        if font_info:
            key_chars = font_info.get("key_characteristics", [])
            if key_chars:
                analysis_parts.append(f"{font_name}的主要特征是：{key_chars[0]}。")
        
        confidence_percent = confidence * 100
        if confidence_percent >= 70:
            analysis_parts.append("本次识别置信度较高，结果较为可靠。")
        elif confidence_percent >= 40:
            analysis_parts.append("本次识别置信度中等，建议参考相似字体进行比对。")
        else:
            analysis_parts.append("本次识别置信度较低，建议提供更多特征描述。")
        
        return "".join(analysis_parts)

    def _find_similar_fonts(self, primary_font, all_results):
        """
        查找相似字体
        
        参数:
            primary_font: 主要识别结果
            all_results: 所有识别结果
            
        返回:
            相似字体列表
        """
        similarity_map = {
            "楷书": [
                {"font": "行书", "differences": "行书笔画有连带，楷书笔画分明；行书结构更自由，楷书结构规整。"},
                {"font": "隶书", "differences": "隶书有蚕头燕尾，结构扁方；楷书横平竖直，结构方正。"}
            ],
            "行书": [
                {"font": "楷书", "differences": "楷书笔画独立，结构规整；行书笔画连带，结构灵活。"},
                {"font": "草书", "differences": "草书高度简化、符号化；行书保留较多楷书特征，辨识度更高。"}
            ],
            "草书": [
                {"font": "行书", "differences": "行书有一定辨识度，保留部分楷书特征；草书高度简化，辨识度低。"},
                {"font": "楷书", "differences": "楷书工整规范，笔画分明；草书连绵不断，符号化程度高。"}
            ],
            "隶书": [
                {"font": "楷书", "differences": "楷书横平竖直，无波磔；隶书有蚕头燕尾，结构扁方。"},
                {"font": "篆书", "differences": "篆书笔画圆润均匀，结构对称；隶书有明显波磔，横向取势。"}
            ],
            "篆书": [
                {"font": "隶书", "differences": "隶书有蚕头燕尾，笔画有粗细变化；篆书笔画均匀圆润，无明显顿笔。"},
                {"font": "楷书", "differences": "楷书有方笔、顿笔，结构方正；篆书圆润对称，纵向长方。"}
            ]
        }

        similar_fonts = similarity_map.get(primary_font, [])
        
        results_dict = {r["font_name"]: r for r in all_results}
        enhanced_similar = []
        
        for similar in similar_fonts:
            font_name = similar["font"]
            result = results_dict.get(font_name, {})
            enhanced_similar.append({
                "font_name": font_name,
                "confidence": round(result.get("confidence", 0) * 100, 2),
                "differences": similar["differences"],
                "font_info": get_font(font_name)
            })
        
        return enhanced_similar
