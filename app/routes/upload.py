"""全銀フォーマット変換ルート

app/filesディレクトリ内の顧客データを全銀フォーマットに変換する機能を提供
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
import os
from datetime import datetime
from app.utils.zengin import ZenginConverter, ZenginFormatError


upload_bp = Blueprint('upload', __name__, url_prefix='/upload')


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename: str) -> bool:
    """Excelファイルかどうかをチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/')
def index():
    """全銀フォーマット変換画面を表示"""
    return render_template('upload/index.html')


@upload_bp.route('/convert', methods=['POST'])
def convert():
    """app/filesディレクトリ内のExcelファイルを全銀フォーマットに変換"""
    try:
        # app/filesディレクトリ内のExcelファイルを探す
        files_dir = os.path.join(current_app.root_path, 'files')
        current_app.logger.info(f'filesディレクトリを検索: {files_dir}')
        
        if not os.path.exists(files_dir):
            flash('filesディレクトリが存在しません', 'error')
            current_app.logger.error(f'filesディレクトリが存在しません: {files_dir}')
            return redirect(url_for('upload.index'))
        
        # Excelファイルを検索
        excel_files = []
        for filename in os.listdir(files_dir):
            if allowed_file(filename):
                excel_files.append(filename)
        
        current_app.logger.info(f'見つかったExcelファイル: {excel_files}')
        
        if not excel_files:
            flash('filesディレクトリにExcelファイル（.xlsx, .xls）が見つかりません', 'error')
            return redirect(url_for('upload.index'))
        
        # 最初のExcelファイルを使用（複数ある場合は最初のもの）
        excel_filename = excel_files[0]
        excel_path = os.path.join(files_dir, excel_filename)
        current_app.logger.info(f'読み込むExcelファイル: {excel_path}')
        
        # 依頼人情報を取得（オプション）
        requester_code = request.form.get('requester_code', '').strip()
        requester_name = request.form.get('requester_name', '').strip()
        sheet_name = request.form.get('sheet_name', '').strip() or None
        
        current_app.logger.info(f'変換パラメータ - シート名: {sheet_name}, 依頼人コード: {requester_code}, 依頼人名: {requester_name}')
        
        # 全銀フォーマットに変換
        try:
            current_app.logger.info('全銀フォーマット変換処理を開始します...')
            records = ZenginConverter.convert_excel_to_zengin(
                excel_path,
                sheet_name=sheet_name,
                requester_code=requester_code,
                requester_name=requester_name
            )
            current_app.logger.info(f'変換成功: {len(records)}件のレコードを生成')
        except ZenginFormatError as e:
            error_msg = str(e)
            flash(f'変換エラー: {error_msg}', 'error')
            current_app.logger.error(f'変換エラー: {error_msg}')
            return redirect(url_for('upload.index'))
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f'変換処理中にエラーが発生しました: {str(e)}'
            flash(error_msg, 'error')
            current_app.logger.error(f'{error_msg}\n{error_detail}')
            return redirect(url_for('upload.index'))
        
        # 出力ファイル名を生成
        output_filename = f"zengin_{datetime.now().strftime('%Y%m%d')}.txt"
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
        current_app.logger.info(f'出力ファイル: {output_path}')
        
        # Shift-JISエンコーディングでファイルに書き込み
        try:
            with open(output_path, 'w', encoding='shift_jis', newline='\r\n') as f:
                for record in records:
                    f.write(record + '\n')
            current_app.logger.info(f'ファイル書き込み完了: {output_path}')
        except UnicodeEncodeError as e:
            error_msg = f'文字エンコーディングエラー: {str(e)}'
            flash(error_msg, 'error')
            current_app.logger.error(error_msg)
            return redirect(url_for('upload.index'))
        
        # ダウンロード用のファイルを返す
        current_app.logger.info(f'ダウンロード開始: {output_filename}')
        try:
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='text/plain; charset=shift_jis'
            )
            current_app.logger.info(f'ダウンロードレスポンス作成完了: {output_filename}')
            return response
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f'ファイルダウンロードエラー: {str(e)}'
            current_app.logger.error(f'{error_msg}\n{error_detail}')
            flash(error_msg, 'error')
            return redirect(url_for('upload.index'))
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f'変換処理エラー: {str(e)}\n{error_detail}')
        flash(f'予期しないエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('upload.index'))

