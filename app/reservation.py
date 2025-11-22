"""
予約機能コントローラ

予約のCRUD機能を提供するBlueprint
"""
from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, abort, jsonify, request, current_app, session
from .models import ExperienceProgram, Reservation # ReservationFormのインポートを削除
from .forms import ReservationForm # 新しくforms.pyからインポート
from . import db
from sqlalchemy import func

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/')
def index():
    """体験プログラムの一覧を表示する"""
    programs = ExperienceProgram.query.order_by(ExperienceProgram.id).all()
    return render_template('index.html', programs=programs)


@reservation_bp.route('/create', methods=['GET', 'POST'], defaults={'program_id': None})
@reservation_bp.route('/create/<int:program_id>', methods=['GET', 'POST'])
def create(program_id=None):
    """予約を作成する"""
    try:
        program = db.session.get(ExperienceProgram, program_id) if program_id else None
        
        # 体験プログラムの選択肢を準備
        program_choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
        
        # フォームを作成
        form = ReservationForm()
        form.program_id.choices = program_choices
        
        # カレンダーから遷移した場合（programが指定されている場合）、
        # program_idはhiddenフィールドで送信されるため、SelectFieldのバリデーションを無効化する
        if program:
            form.program_id.validators = []
        
        # フォームのバリデーション結果を保持する変数
        is_valid = False
        
        if request.method == 'GET':
            if program:
                form.program_id.data = program.id
            # カレンダーからの日付を受け取る
            if 'date' in request.args:
                date_str = request.args.get('date')
                try:
                    # 日付文字列をDateオブジェクトに変換
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    form.reservation_date.data = date_obj
                except (ValueError, TypeError) as e:
                    flash('日付の形式が正しくありません。', 'error')
        elif request.method == 'POST':
            # POSTリクエストの場合、hiddenフィールドからprogram_idを取得してフォームに設定
            # 優先順位: URLパラメータ > hiddenフィールド
            post_program_id = program_id or request.form.get('program_id', type=int)
            if post_program_id:
                form.program_id.data = post_program_id
            
            # フォームのバリデーションを実行（1回だけ）
            try:
                is_valid = form.validate_on_submit()
            except Exception as e:
                print(f'[ERROR] バリデーション実行中にエラー: {str(e)}')
                import traceback
                print(traceback.format_exc())
                is_valid = False
        
        if is_valid:
            try:
                # フォームから送信されたprogram_idでプログラムを再取得
                # hiddenフィールドからの値も考慮する
                selected_program_id = form.program_id.data or request.form.get('program_id', type=int) or program_id
                if not selected_program_id:
                    flash('プログラムを選択してください。', 'error')
                    form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
                    return render_template('reservations/create.html', form=form, program=program)
                
                selected_program = db.session.get(ExperienceProgram, selected_program_id)
                if not selected_program:
                    flash('指定された体験プログラムが見つかりません。', 'error')
                    form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
                    return render_template('reservations/create.html', form=form, program=program)
                # 定員チェック
                existing_reservations = Reservation.query.filter_by(
                    program_id=selected_program_id,
                    reservation_date=form.reservation_date.data
                ).all()
                
                total_participants = sum(r.number_of_participants for r in existing_reservations)
                if total_participants + form.number_of_participants.data > selected_program.capacity:
                    flash(f'この日の予約が満席です。（残り: {selected_program.capacity - total_participants}名）', 'error')
                    return render_template('reservations/create.html', form=form, program=program)
                
                # 確認画面にリダイレクト（セッションにデータを保存）
                session['reservation_data'] = {
                    'program_id': selected_program_id,
                    'name': form.name.data,
                    'email': form.email.data,
                    'phone_number': form.phone_number.data,
                    'reservation_date': form.reservation_date.data.isoformat(),
                    'number_of_participants': form.number_of_participants.data
                }
                return redirect(url_for('reservation.confirm'))
                
            except Exception as e:
                db.session.rollback()
                import traceback
                error_msg = str(e)
                error_traceback = traceback.format_exc()
                # ログに詳細なエラー情報を出力
                current_app.logger.error(f'予約作成エラー: {error_msg}')
                current_app.logger.error(error_traceback)
                # コンソールにも出力（開発時）
                print(f'[ERROR] 予約作成エラー: {error_msg}')
                print(f'[ERROR] トレースバック:\n{error_traceback}')
                # エラーメッセージが長すぎる場合は短縮
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + '...'
                flash(f'予約の作成中にエラーが発生しました: {error_msg}', 'error')
        
        # バリデーションエラーがある場合、エラーメッセージを表示
        # validate_on_submit()がFalseを返した場合、form.errorsにエラーが含まれている
        if request.method == 'POST' and not is_valid and form.errors:
            for field_name, errors in form.errors.items():
                try:
                    field = getattr(form, field_name, None)
                    if field and hasattr(field, 'label') and field.label:
                        field_label = field.label.text
                    else:
                        # フィールド名を人間が読める形式に変換
                        field_label = field_name.replace('_', ' ').title()
                    for error in errors:
                        flash(f'{field_label}: {error}', 'error')
                except Exception as e:
                    # フィールドが取得できない場合でもエラーメッセージを表示
                    for error in errors:
                        flash(f'{field_name}: {error}', 'error')
        
        # フォームの選択肢を再設定（エラー時にも必要）
        form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
        
        return render_template('reservations/create.html', form=form, program=program)
    
    except Exception as e:
        # 予期しないエラーをキャッチ
        import traceback
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        current_app.logger.error(f'予約フォーム表示エラー: {error_msg}')
        current_app.logger.error(error_traceback)
        print(f'[ERROR] 予約フォーム表示エラー: {error_msg}')
        print(f'[ERROR] トレースバック:\n{error_traceback}')
        flash(f'エラーが発生しました: {error_msg[:100]}', 'error')
        # エラー時でもフォームを表示できるようにする
        try:
            form = ReservationForm()
            form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
            program = db.session.get(ExperienceProgram, program_id) if program_id else None
            return render_template('reservations/create.html', form=form, program=program)
        except:
            # フォームも作成できない場合は、エラーページを返す
            abort(500)


@reservation_bp.route('/confirm', methods=['GET', 'POST'])
def confirm():
    """予約確認画面"""
    # セッションから予約データを取得
    reservation_data = session.get('reservation_data')
    if not reservation_data:
        flash('予約情報が見つかりません。最初からやり直してください。', 'error')
        return redirect(url_for('reservation.index'))
    
    # プログラム情報を取得
    program = db.session.get(ExperienceProgram, reservation_data['program_id'])
    if not program:
        flash('体験プログラムが見つかりません。', 'error')
        session.pop('reservation_data', None)
        return redirect(url_for('reservation.index'))
    
    # フォームを作成（編集可能にするため）
    form = ReservationForm()
    form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
    
    # 日付オブジェクトを作成（テンプレート用）
    reservation_date_obj = None
    try:
        if isinstance(reservation_data['reservation_date'], str):
            reservation_date_obj = datetime.fromisoformat(reservation_data['reservation_date']).date()
        else:
            reservation_date_obj = reservation_data['reservation_date']
    except (ValueError, KeyError):
        pass
    
    # 決定ボタンが押された場合（最初にチェック）
    if request.method == 'POST' and 'confirm' in request.form:
        # 確認画面ではセッションデータから直接予約を作成（既にバリデーション済み）
        try:
            # セッションデータから値を取得
            program_id = reservation_data['program_id']
            name = reservation_data['name']
            email = reservation_data['email']
            phone_number = reservation_data['phone_number']
            reservation_date_str = reservation_data['reservation_date']
            number_of_participants = reservation_data['number_of_participants']
            
            # 日付を変換
            if isinstance(reservation_date_str, str):
                reservation_date = datetime.fromisoformat(reservation_date_str).date()
            else:
                reservation_date = reservation_date_str
            
            # プログラムを再取得
            selected_program = db.session.get(ExperienceProgram, program_id)
            if not selected_program:
                flash('指定された体験プログラムが見つかりません。', 'error')
                return render_template('reservations/confirm.html', 
                                     form=form, 
                                     program=program,
                                     reservation_data=reservation_data,
                                     reservation_date_obj=reservation_date_obj)
            
            # 定員チェック
            existing_reservations = Reservation.query.filter_by(
                program_id=program_id,
                reservation_date=reservation_date
            ).all()
            
            total_participants = sum(r.number_of_participants for r in existing_reservations)
            if total_participants + number_of_participants > selected_program.capacity:
                flash(f'この日の予約が満席です。（残り: {selected_program.capacity - total_participants}名）', 'error')
                return render_template('reservations/confirm.html', 
                                     form=form, 
                                     program=selected_program,
                                     reservation_data=reservation_data,
                                     reservation_date_obj=reservation_date_obj)
            
            # 予約を作成
            reservation = Reservation(
                program_id=program_id,
                name=name,
                email=email,
                phone_number=phone_number,
                reservation_date=reservation_date,
                number_of_participants=number_of_participants
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            # セッションをクリア
            session.pop('reservation_data', None)
            
            flash('予約が完了しました。', 'success')
            return redirect(url_for('reservation.index'))
            
        except Exception as e:
            db.session.rollback()
            import traceback
            error_msg = str(e)
            current_app.logger.error(f'予約作成エラー: {error_msg}')
            current_app.logger.error(traceback.format_exc())
            flash(f'予約の作成中にエラーが発生しました: {error_msg[:100]}', 'error')
            # エラー時は確認画面を再表示
            return render_template('reservations/confirm.html', 
                                 form=form, 
                                 program=program,
                                 reservation_data=reservation_data,
                                 reservation_date_obj=reservation_date_obj)
    
    # セッションデータをフォームに設定（表示用）
    form.program_id.data = reservation_data['program_id']
    form.name.data = reservation_data['name']
    form.email.data = reservation_data['email']
    form.phone_number.data = reservation_data['phone_number']
    form.reservation_date.data = reservation_date_obj or datetime.fromisoformat(reservation_data['reservation_date']).date()
    form.number_of_participants.data = reservation_data['number_of_participants']
    
    # バリデーションエラーがある場合（予約確定ボタン以外のPOSTリクエスト時のみ）
    if request.method == 'POST' and 'confirm' not in request.form and form.errors:
        for field_name, errors in form.errors.items():
            try:
                field = getattr(form, field_name, None)
                if field and hasattr(field, 'label') and field.label:
                    field_label = field.label.text
                else:
                    field_label = field_name.replace('_', ' ').title()
                for error in errors:
                    flash(f'{field_label}: {error}', 'error')
            except Exception as e:
                for error in errors:
                    flash(f'{field_name}: {error}', 'error')
    
    return render_template('reservations/confirm.html', 
                         form=form, 
                         program=program,
                         reservation_data=reservation_data,
                         reservation_date_obj=reservation_date_obj)


@reservation_bp.route('/show/<int:id>')
def show(id):
    """予約の詳細を表示する"""
    reservation = db.session.get(Reservation, id)
    if not reservation:
        abort(404)
    
    return render_template('reservations/show.html', reservation=reservation)


@reservation_bp.route('/list')
def list_reservations():
    """予約一覧を表示する（管理用）"""
    reservations = Reservation.query.order_by(Reservation.reservation_date.desc()).all()
    return render_template('reservations/list.html', reservations=reservations)


@reservation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """予約を編集する"""
    reservation = db.session.get(Reservation, id)
    if not reservation:
        abort(404)
    
    form = ReservationForm(obj=reservation)
    form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
    
    if form.validate_on_submit():
        try:
            program = db.session.get(ExperienceProgram, form.program_id.data)
            if not program:
                flash('指定された体験プログラムが見つかりません。', 'error')
                return render_template('reservations/edit.html', form=form, reservation=reservation)
            
            # 定員チェック（自分自身を除く）
            existing_reservations = Reservation.query.filter(
                Reservation.program_id == form.program_id.data,
                Reservation.reservation_date == form.reservation_date.data,
                Reservation.id != id
            ).all()
            
            total_participants = sum(r.number_of_participants for r in existing_reservations)
            if total_participants + form.number_of_participants.data > program.capacity:
                flash(f'この日の予約が満席です。（残り: {program.capacity - total_participants}名）', 'error')
                return render_template('reservations/edit.html', form=form, reservation=reservation)
            
            # 予約を更新
            reservation.program_id = form.program_id.data
            reservation.name = form.name.data
            reservation.email = form.email.data
            reservation.phone_number = form.phone_number.data
            reservation.reservation_date = form.reservation_date.data
            reservation.number_of_participants = form.number_of_participants.data
            
            db.session.commit()
            
            flash('予約を更新しました。', 'success')
            return redirect(url_for('reservation.show', id=reservation.id))
            
        except Exception as e:
            db.session.rollback()
            flash('予約の更新中にエラーが発生しました。', 'error')
    
    return render_template('reservations/edit.html', form=form, reservation=reservation)


@reservation_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """予約を削除する"""
    reservation = db.session.get(Reservation, id)
    if not reservation:
        abort(404)
    
    try:
        db.session.delete(reservation)
        db.session.commit()
        flash('予約を削除しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash('予約の削除中にエラーが発生しました。', 'error')
    
    return redirect(url_for('reservation.list_reservations'))


@reservation_bp.route('/api/events')
def api_events():
    """カレンダー表示用の予約データをJSONで返す"""
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify([])

    start_date = date.fromisoformat(start_str.split('T')[0])
    end_date = date.fromisoformat(end_str.split('T')[0])

    programs = ExperienceProgram.query.all()
    
    # 期間内の予約人数を事前に集計
    reservations_count = db.session.query(
        Reservation.program_id,
        Reservation.reservation_date,
        func.sum(Reservation.number_of_participants).label('total_participants')
    ).filter(
        Reservation.reservation_date.between(start_date, end_date)
    ).group_by(
        Reservation.program_id,
        Reservation.reservation_date
    ).all()

    # 高速アクセスのために辞書に変換
    reservation_map = {(r.program_id, r.reservation_date): r.total_participants for r in reservations_count}

    events = []
    for day in range((end_date - start_date).days):
        current_date = start_date + timedelta(days=day)
        for program in programs:
            booked_participants = reservation_map.get((program.id, current_date), 0)
            remaining = program.capacity - booked_participants
            is_full = remaining <= 0
            has_reservations = booked_participants > 0
            
            # プログラム名をカレンダー表示用に短縮
            display_name = program.name
            if 'ハンカチ' in program.name:
                display_name = 'ハンカチ'
            elif '天然藍' in program.name:
                display_name = '天然藍'

            # URLを生成（満席でない場合のみ）
            event_url = None
            if not is_full:
                event_url = url_for('reservation.create', program_id=program.id, _external=False) + f"?date={current_date.isoformat()}"
            
            # 色の決定: 満席=赤、予約ありで余裕あり=緑、予約なし=青
            if is_full:
                bg_color = '#ef4444'  # 赤
                border_color = '#ef4444'
            elif has_reservations:
                bg_color = '#22c55e'  # 緑（予約が入っていて余裕がある）
                border_color = '#22c55e'
            else:
                bg_color = '#3b82f6'  # 青（予約が入っていない）
                border_color = '#3b82f6'
            
            events.append({
                'title': f"{display_name}: {'受付終了' if is_full else f'残り{remaining}名'}",
                'start': current_date.isoformat(),
                'url': event_url,
                'backgroundColor': bg_color,
                'borderColor': border_color,
                'classNames': ['cursor-pointer'] if not is_full else ['cursor-not-allowed'],
                'extendedProps': {
                    'program_id': program.id,
                    'program_name': program.name,
                    'date': current_date.isoformat()
                }
            })

    return jsonify(events)
