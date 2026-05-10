"""
API路由模块
定义Flask应用的所有API接口
"""

import json
import logging
from datetime import datetime
from flask import request, jsonify, make_response

from app import app
from app.feature_extractor import FeatureExtractor
from app.font_recognizer import FontRecognizer
from app.font_library import get_all_fonts, get_font, get_font_names
from app.database import get_database
from app.report_generator import ReportGenerator
from app.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

feature_extractor = FeatureExtractor()
font_recognizer = FontRecognizer()
report_generator = ReportGenerator()
image_processor = ImageProcessor()
db = get_database()


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    返回:
        服务状态信息
    """
    return jsonify({
        'status': 'ok',
        'service': '书法字体识别器',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/fonts', methods=['GET'])
def list_fonts():
    """
    获取所有字体信息
    
    返回:
        所有字体列表
    """
    fonts = get_all_fonts()
    return jsonify({
        'success': True,
        'count': len(fonts),
        'fonts': fonts
    })


@app.route('/api/fonts/<font_name>', methods=['GET'])
def get_font_detail(font_name):
    """
    获取指定字体的详细信息
    
    参数:
        font_name: 字体名称
        
    返回:
        字体详细信息
    """
    font_info = get_font(font_name)
    if font_info:
        return jsonify({
            'success': True,
            'font': font_info
        })
    else:
        return jsonify({
            'success': False,
            'message': f'未找到字体: {font_name}'
        }), 404


@app.route('/api/fonts/names', methods=['GET'])
def list_font_names():
    """
    获取所有字体名称列表
    
    返回:
        字体名称列表
    """
    names = get_font_names()
    return jsonify({
        'success': True,
        'font_names': names
    })


@app.route('/api/recognize', methods=['POST'])
def recognize_font():
    """
    识别书法字体
    
    请求体:
        {
            "description": "字体特征描述文本"
        }
        
    返回:
        识别结果
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体为空'
            }), 400

        description = data.get('description', '').strip()
        if not description:
            return jsonify({
                'success': False,
                'message': '请输入字体特征描述'
            }), 400

        logger.info(f"收到识别请求: {description[:100]}...")

        features = feature_extractor.extract_features(description)

        recognition_result = font_recognizer.recognize(features, description)

        primary = recognition_result.get('primary_result', {})
        font_name = primary.get('font_name', '未知')
        confidence = primary.get('confidence', 0)

        record_id = db.add_recognition(
            input_text=description,
            recognized_font=font_name,
            confidence=confidence,
            result_json=json.dumps(recognition_result, ensure_ascii=False)
        )

        return jsonify({
            'success': True,
            'record_id': record_id,
            'result': recognition_result
        })

    except Exception as e:
        logger.error(f"识别出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'识别出错: {str(e)}'
        }), 500


@app.route('/api/recognize/image', methods=['POST'])
def recognize_font_by_image():
    """
    通过上传图片识别书法字体
    
    请求体:
        multipart/form-data格式，包含image字段
        
    返回:
        识别结果
    """
    try:
        from app.image_processor import PIL_AVAILABLE
        if not PIL_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '图片识别功能需要安装Pillow和NumPy库。请运行: pip3 install Pillow numpy'
            }), 503

        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': '请上传图片文件'
            }), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'message': '未选择文件'
            }), 400

        logger.info(f"收到图片识别请求: {image_file.filename}")

        is_valid, error_msg = image_processor.validate_image(image_file)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400

        image_features = image_processor.process_image(image_file)

        image_file.seek(0)
        image_base64 = image_processor.image_to_base64(image_file)

        generated_description = image_processor.generate_description(image_features)

        text_features = feature_extractor.extract_features(generated_description)

        font_prediction = image_features.get('font_prediction', {})
        image_scores = font_prediction.get('scores', {})
        text_scores = text_features.get('scores', {})

        combined_scores = {}
        all_fonts = ["楷书", "行书", "草书", "隶书", "篆书"]
        for font in all_fonts:
            image_score = image_scores.get(font, 0)
            text_score = text_scores.get(font, 0)
            combined_scores[font] = image_score * 0.7 + text_score * 0.3

        total_score = sum(combined_scores.values())
        if total_score > 0:
            combined_results = []
            for font, score in combined_scores.items():
                combined_results.append({
                    'font_name': font,
                    'confidence': score / total_score,
                    'score': score
                })
            combined_results.sort(key=lambda x: x['confidence'], reverse=True)

            primary_font = combined_results[0]['font_name']
            primary_confidence = combined_results[0]['confidence']

            primary_result = {
                'font_name': primary_font,
                'confidence': round(primary_confidence * 100, 2),
                'font_info': get_font(primary_font),
                'matched_keywords': text_features.get('matched_keywords', []),
                'analysis': f"根据图片分析，该书法作品最可能是{primary_font}。图片特征分析显示：{generated_description}"
            }
        else:
            primary_result = {
                'font_name': '楷书',
                'confidence': 20.0,
                'font_info': get_font('楷书'),
                'matched_keywords': [],
                'analysis': '图片特征不明显，建议提供更清晰的图片或补充文字描述。'
            }
            combined_results = [{'font_name': f, 'confidence': 0.2, 'score': 0} for f in all_fonts]

        similar_fonts = font_recognizer._find_similar_fonts(
            primary_result['font_name'],
            combined_results
        )

        recognition_result = {
            'primary_result': primary_result,
            'all_results': combined_results,
            'similar_fonts': similar_fonts,
            'image_features': {
                'image_info': image_features.get('image_info', {}),
                'color_features': image_features.get('color_features', {}),
                'texture_features': image_features.get('texture_features', {}),
                'stroke_features': image_features.get('stroke_features', {}),
                'structure_features': image_features.get('structure_features', {})
            },
            'generated_description': generated_description,
            'recognition_type': 'image'
        }

        record_id = db.add_recognition(
            input_text=f"[图片识别] {generated_description}",
            recognized_font=primary_result['font_name'],
            confidence=primary_result['confidence'],
            result_json=json.dumps(recognition_result, ensure_ascii=False)
        )

        return jsonify({
            'success': True,
            'record_id': record_id,
            'result': recognition_result,
            'image_preview': f"data:image/png;base64,{image_base64}"
        })

    except Exception as e:
        logger.error(f"图片识别出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'图片识别出错: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    获取识别历史记录
    
    查询参数:
        limit: 返回记录数限制，默认50
        offset: 偏移量，默认0
        
    返回:
        历史记录列表
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        history = db.get_recognition_history(limit=limit, offset=offset)
        total = db.get_recognition_count()

        return jsonify({
            'success': True,
            'total': total,
            'count': len(history),
            'limit': limit,
            'offset': offset,
            'history': history
        })

    except Exception as e:
        logger.error(f"获取历史记录出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取历史记录出错: {str(e)}'
        }), 500


@app.route('/api/history/<int:record_id>', methods=['GET'])
def get_history_detail(record_id):
    """
    获取指定历史记录详情
    
    参数:
        record_id: 记录ID
        
    返回:
        历史记录详情
    """
    try:
        record = db.get_recognition_by_id(record_id)
        if not record:
            return jsonify({
                'success': False,
                'message': f'未找到记录: {record_id}'
            }), 404

        result_json = record.get('result_json')
        if result_json:
            try:
                record['result'] = json.loads(result_json)
            except:
                record['result'] = None

        return jsonify({
            'success': True,
            'record': record
        })

    except Exception as e:
        logger.error(f"获取历史详情出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取历史详情出错: {str(e)}'
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取识别统计信息
    
    返回:
        统计信息
    """
    try:
        total_count = db.get_recognition_count()
        font_stats = db.get_font_recognition_stats()

        return jsonify({
            'success': True,
            'total_recognitions': total_count,
            'font_statistics': font_stats
        })

    except Exception as e:
        logger.error(f"获取统计信息出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取统计信息出错: {str(e)}'
        }), 500


@app.route('/api/export/<int:record_id>', methods=['GET'])
def export_report(record_id):
    """
    导出识别报告
    
    参数:
        record_id: 记录ID
        
    返回:
        文本格式报告文件
    """
    try:
        record = db.get_recognition_by_id(record_id)
        if not record:
            return jsonify({
                'success': False,
                'message': f'未找到记录: {record_id}'
            }), 404

        result_json = record.get('result_json')
        input_text = record.get('input_text', '')

        if result_json:
            recognition_result = json.loads(result_json)
        else:
            return jsonify({
                'success': False,
                'message': '记录数据不完整'
            }), 400

        report_content = report_generator.generate_text_report(
            recognition_result=recognition_result,
            input_text=input_text
        )

        primary = recognition_result.get('primary_result', {})
        font_name = primary.get('font_name', '未知')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"字体识别报告_{font_name}_{timestamp}.txt"

        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        logger.info(f"导出报告: {filename}")
        return response

    except Exception as e:
        logger.error(f"导出报告出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导出报告出错: {str(e)}'
        }), 500


@app.route('/api/export', methods=['POST'])
def export_report_direct():
    """
    直接导出当前识别报告（无需保存到数据库）
    
    请求体:
        {
            "result": 识别结果字典,
            "input_text": "原始输入文本"
        }
        
    返回:
        文本格式报告文件
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体为空'
            }), 400

        recognition_result = data.get('result', {})
        input_text = data.get('input_text', '')

        if not recognition_result:
            return jsonify({
                'success': False,
                'message': '缺少识别结果数据'
            }), 400

        report_content = report_generator.generate_text_report(
            recognition_result=recognition_result,
            input_text=input_text
        )

        primary = recognition_result.get('primary_result', {})
        font_name = primary.get('font_name', '未知')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"字体识别报告_{font_name}_{timestamp}.txt"

        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        logger.info(f"导出报告: {filename}")
        return response

    except Exception as e:
        logger.error(f"导出报告出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导出报告出错: {str(e)}'
        }), 500
