"""
ファイルアップロードルーティング

顧客データファイルのアップロード処理を提供します。
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Customer, TransferHistory
from app.forms import CustomerUploadForm
from app.utils.file_processor import process_uploaded_file
import os
from datetime import datetime

# Blueprintの作成
upload_bp = Blueprint('upload', __name__, url_prefix='/upload')


@upload_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    ファイルアップロード画面

    Returns:
        str: アップロード画面のHTML
    """
    form = CustomerUploadForm()
    
    if form.validate_on_submit():
        try:
            # ファイルを取得
            file = form.file.data
            
            # ファイル名を安全に処理
            filename = secure_filename(file.filename)
            
            # ファイルサイズのチェック（最大10MB）
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if file_size > MAX_FILE_SIZE:
                flash('ファイルサイズが大きすぎます。最大10MBまでアップロードできます。', 'error')
                return render_template('upload/index.html', form=form)
            
            # ファイル処理
            df, errors = process_uploaded_file(file)
            
            if errors:
                # エラーがある場合はエラーメッセージを表示
                for error in errors:
                    flash(error, 'error')
                return render_template('upload/index.html', form=form)
            
            if df.empty:
                flash('有効なデータが見つかりませんでした。', 'error')
                return render_template('upload/index.html', form=form)
            
            # データベースに保存
            saved_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    # 顧客データを作成
                    customer = Customer(
                        customer_name=row['customer_name'],
                        bank_code=row['bank_code'],
                        branch_code=row['branch_code'],
                        account_type=row['account_type'],
                        account_number=row['account_number'],
                        transfer_amount=row['transfer_amount']
                    )
                    
                    # バリデーション
                    validation_errors = customer.validate()
                    if validation_errors:
                        error_count += 1
                        for error in validation_errors:
                            flash(f'行{_ + 1}: {error}', 'error')
                        continue
                    
                    # データベースに保存
                    db.session.add(customer)
                    saved_count += 1
                    
                except Exception as e:
                    error_count += 1
                    flash(f'行{_ + 1}: データの保存中にエラーが発生しました: {str(e)}', 'error')
                    current_app.logger.error(f'Error saving customer data: {str(e)}')
            
            # コミット
            try:
                db.session.commit()
                
                # アップロード履歴を保存
                history = TransferHistory(
                    file_name=filename,
                    record_count=saved_count
                )
                db.session.add(history)
                db.session.commit()
                
                # 成功メッセージ
                flash(f'{saved_count}件のデータを正常にアップロードしました。', 'success')
                if error_count > 0:
                    flash(f'{error_count}件のデータでエラーが発生しました。', 'warning')
                
                # アップロード完了後、一覧画面にリダイレクト（将来的に実装）
                return redirect(url_for('upload.index'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'データベースへの保存中にエラーが発生しました: {str(e)}', 'error')
                current_app.logger.error(f'Error committing to database: {str(e)}')
                return render_template('upload/index.html', form=form)
        
        except Exception as e:
            flash(f'ファイルの処理中にエラーが発生しました: {str(e)}', 'error')
            current_app.logger.error(f'Error processing file: {str(e)}')
            return render_template('upload/index.html', form=form)
    
    return render_template('upload/index.html', form=form)

