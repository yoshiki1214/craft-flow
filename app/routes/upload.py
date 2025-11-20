"""全銀フォーマット変換ルート

app/filesディレクトリ内の顧客データを全銀フォーマットに変換する機能を提供
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime
from app.utils.zengin import ZenginConverter, ZenginFormatError


upload_bp = Blueprint('upload', __name__, url_prefix='/upload')


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename: str) -> bool:
    """Excelファイルかどうかをチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_datetime_from_filename(filename: str, output_dir: str = None) -> datetime:
    """
    ファイル名から日時を抽出
    
    Args:
        filename: zengin_YYYYMMDD_HHMMSS.txt形式のファイル名
        output_dir: 出力ディレクトリのパス（オプション）
        
    Returns:
        抽出された日時（datetimeオブジェクト）、抽出できない場合はファイルの作成日時
    """
    # zengin_YYYYMMDD_HHMMSS.txt形式のパターン
    pattern = r'zengin_(\d{8})_(\d{6})\.txt'
    match = re.match(pattern, filename)
    
    if match:
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS
        
        try:
            # 日時文字列をパース
            dt = datetime.strptime(f'{date_str}_{time_str}', '%Y%m%d_%H%M%S')
            return dt
        except ValueError:
            # パースに失敗した場合はファイルの作成日時を使用
            pass
    
    # パターンに一致しない、またはパースに失敗した場合はファイルの作成日時を使用
    if output_dir:
        try:
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                timestamp = os.path.getctime(filepath)
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass
    
    # デフォルト値として現在の日時を返す
    return datetime.now()


def get_conversion_history() -> list:
    """
    output/ディレクトリ内の全銀フォーマットファイルの履歴を取得
    
    Returns:
        ファイル情報のリスト（新しい順にソート）
        各要素は {'filename': str, 'datetime': datetime, 'formatted_datetime': str} の形式
    """
    output_dir = current_app.config.get('OUTPUT_FOLDER', os.path.join(current_app.instance_path, 'outputs'))
    
    if not os.path.exists(output_dir):
        return []
    
    history = []
    
    # output/ディレクトリ内のファイルを取得
    for filename in os.listdir(output_dir):
        # .txtファイルのみを対象
        if filename.endswith('.txt') and filename.startswith('zengin_'):
            filepath = os.path.join(output_dir, filename)
            
            # ファイルのみを対象（ディレクトリは除外）
            if os.path.isfile(filepath):
                dt = extract_datetime_from_filename(filename, output_dir)
                
                # 日時をフォーマット（YYYY年MM月DD日 HH:MM:SS）
                formatted_dt = dt.strftime('%Y年%m月%d日 %H:%M:%S')
                
                history.append({
                    'filename': filename,
                    'datetime': dt,
                    'formatted_datetime': formatted_dt
                })
    
    # 新しい順にソート（datetimeで降順）
    history.sort(key=lambda x: x['datetime'], reverse=True)
    
    return history


@upload_bp.route('/')
def index():
    """全銀フォーマット変換画面を表示（最新保存ファイルのダウンロードリンク含む）"""
    from flask import session
    
    # セッションから最新保存ファイル名を取得
    last_filename = session.pop('last_output_filename', None)
    last_path = session.pop('last_output_path', None)
    
    return render_template('upload/index.html', 
                         last_filename=last_filename,
                         last_path=last_path)


@upload_bp.route('/history')
def history():
    """変換履歴一覧画面を表示"""
    try:
        history_list = get_conversion_history()
        return render_template('upload/history.html', history=history_list)
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        error_msg = f'履歴取得エラー: {str(e)}'
        current_app.logger.error(f'{error_msg}\n{error_detail}')
        flash(error_msg, 'error')
        return redirect(url_for('upload.index'))


@upload_bp.route('/success')
def success():
    """ファイル保存成功画面を表示"""
    filename = request.args.get('filename', '')
    if not filename:
        flash('ファイル名が指定されていません', 'error')
        return redirect(url_for('upload.index'))
    return render_template('upload/success.html', filename=filename)


@upload_bp.route('/download/<filename>')
def download(filename):
    """保存された全銀フォーマットファイルをダウンロード"""
    try:
        # ファイルパスを構築
        filepath = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
        
        # ファイルの存在確認
        if not os.path.exists(filepath):
            flash(f'ファイルが見つかりません: {filename}', 'error')
            current_app.logger.error(f'ファイルが見つかりません: {filepath}')
            return redirect(url_for('upload.index'))
        
        # セキュリティチェック（ディレクトリトラバーサル対策）
        if not os.path.abspath(filepath).startswith(os.path.abspath(current_app.config['OUTPUT_FOLDER'])):
            flash('不正なファイルパスです', 'error')
            current_app.logger.error(f'不正なファイルパス: {filepath}')
            return redirect(url_for('upload.index'))
        
        # エンコーディングの判定（ファイル名から推測）
        mimetype = 'text/plain; charset=shift_jis'
        if filename.endswith('.txt'):
            # デフォルトはShift-JIS
            mimetype = 'text/plain; charset=shift_jis'
        
        current_app.logger.info(f'ダウンロード開始: {filename}')
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        error_msg = f'ファイルダウンロードエラー: {str(e)}'
        current_app.logger.error(f'{error_msg}\n{error_detail}')
        flash(error_msg, 'error')
        return redirect(url_for('upload.index'))


@upload_bp.route('/convert', methods=['POST'])
def convert():
    """アップロードされたExcelファイルまたはapp/filesディレクトリ内のExcelファイルを全銀フォーマットに変換"""
    try:
        excel_path = None
        uploaded_file = None
        
        # 1. アップロードされたファイルを確認
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                # ファイル名を安全に処理
                filename = secure_filename(file.filename)
                # 一時保存ディレクトリに保存
                upload_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.instance_path, 'uploads'))
                os.makedirs(upload_dir, exist_ok=True)
                
                # 一時ファイルとして保存
                excel_path = os.path.join(upload_dir, filename)
                file.save(excel_path)
                uploaded_file = excel_path
                current_app.logger.info(f'アップロードされたファイルを保存: {excel_path}')
        
        # 2. アップロードファイルがない場合、app/filesディレクトリから検索
        if not excel_path:
            files_dir = os.path.join(current_app.root_path, 'files')
            current_app.logger.info(f'filesディレクトリを検索: {files_dir}')
            
            if not os.path.exists(files_dir):
                flash('Excelファイルをアップロードするか、app/filesディレクトリにExcelファイルを配置してください', 'error')
                current_app.logger.error(f'filesディレクトリが存在しません: {files_dir}')
                return redirect(url_for('upload.index'))
            
            # Excelファイルを検索
            excel_files = []
            for filename in os.listdir(files_dir):
                if allowed_file(filename):
                    excel_files.append(filename)
            
            current_app.logger.info(f'見つかったExcelファイル: {excel_files}')
            
            if not excel_files:
                flash('Excelファイルをアップロードするか、app/filesディレクトリにExcelファイル（.xlsx, .xls）を配置してください', 'error')
                return redirect(url_for('upload.index'))
            
            # 最初のExcelファイルを使用（複数ある場合は最初のもの）
            excel_filename = excel_files[0]
            excel_path = os.path.join(files_dir, excel_filename)
            current_app.logger.info(f'読み込むExcelファイル: {excel_path}')
        
        # ファイルの存在確認
        if not os.path.exists(excel_path):
            flash('Excelファイルが見つかりません', 'error')
            current_app.logger.error(f'Excelファイルが見つかりません: {excel_path}')
            return redirect(url_for('upload.index'))
        
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
            # アップロードされた一時ファイルを削除
            if uploaded_file and os.path.exists(uploaded_file):
                try:
                    os.remove(uploaded_file)
                    current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
                except Exception as del_e:
                    current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(del_e)}')
            return redirect(url_for('upload.index'))
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f'変換処理中にエラーが発生しました: {str(e)}'
            flash(error_msg, 'error')
            current_app.logger.error(f'{error_msg}\n{error_detail}')
            # アップロードされた一時ファイルを削除
            if uploaded_file and os.path.exists(uploaded_file):
                try:
                    os.remove(uploaded_file)
                    current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
                except Exception as del_e:
                    current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(del_e)}')
            return redirect(url_for('upload.index'))
        
        # エンコーディングと改行コードの設定を取得（デフォルト: Shift-JIS, CRLF）
        encoding = request.form.get('encoding', 'shift_jis').lower()
        newline = request.form.get('newline', '\r\n')
        if newline == 'lf':
            newline = '\n'
        elif newline == 'crlf':
            newline = '\r\n'
        
        # 全銀フォーマットファイルを保存
        try:
            output_path, output_filename = ZenginConverter.save_zengin_file(
                records=records,
                output_dir=current_app.config['OUTPUT_FOLDER'],
                encoding=encoding,
                newline=newline
            )
            current_app.logger.info(f'ファイル保存完了: {output_path}')
            
            # 保存成功メッセージとダウンロードリンクを表示するためにセッションに保存
            from flask import session
            session['last_output_filename'] = output_filename
            session['last_output_path'] = output_path
            
            flash(f'全銀フォーマットファイルを保存しました: {output_filename}', 'success')
            current_app.logger.info(f'保存ファイル: {output_filename}')
            
            # アップロードされた一時ファイルを削除
            if uploaded_file and os.path.exists(uploaded_file):
                try:
                    os.remove(uploaded_file)
                    current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
                except Exception as e:
                    current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(e)}')
            
            # トップページにリダイレクト（成功メッセージとダウンロードリンクを表示）
            return redirect(url_for('upload.index'))
            
        except ZenginFormatError as e:
            error_msg = f'ファイル保存エラー: {str(e)}'
            flash(error_msg, 'error')
            current_app.logger.error(error_msg)
            # アップロードされた一時ファイルを削除
            if uploaded_file and os.path.exists(uploaded_file):
                try:
                    os.remove(uploaded_file)
                    current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
                except Exception as del_e:
                    current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(del_e)}')
            return redirect(url_for('upload.index'))
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f'ファイル保存中にエラーが発生しました: {str(e)}'
            flash(error_msg, 'error')
            current_app.logger.error(f'{error_msg}\n{error_detail}')
            # アップロードされた一時ファイルを削除
            if uploaded_file and os.path.exists(uploaded_file):
                try:
                    os.remove(uploaded_file)
                    current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
                except Exception as del_e:
                    current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(del_e)}')
            return redirect(url_for('upload.index'))
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f'変換処理エラー: {str(e)}\n{error_detail}')
        flash(f'予期しないエラーが発生しました: {str(e)}', 'error')
        # アップロードされた一時ファイルを削除
        if 'uploaded_file' in locals() and uploaded_file and os.path.exists(uploaded_file):
            try:
                os.remove(uploaded_file)
                current_app.logger.info(f'一時ファイルを削除: {uploaded_file}')
            except Exception as del_e:
                current_app.logger.warning(f'一時ファイルの削除に失敗: {uploaded_file}, {str(del_e)}')
        return redirect(url_for('upload.index'))

