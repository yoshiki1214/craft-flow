"""
予約機能コントローラ

予約のCRUD機能を提供するBlueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from .models import ExperienceProgram, Reservation
from .forms import ReservationForm
from . import db

reservation_bp = Blueprint('reservation', __name__)


@reservation_bp.route('/')
def index():
    """体験プログラムの一覧を表示する"""
    programs = ExperienceProgram.query.all()
    return render_template('index.html', programs=programs)


@reservation_bp.route('/create/<int:program_id>', methods=['GET', 'POST'])
def create(program_id):
    """予約を作成する"""
    program = db.session.get(ExperienceProgram, program_id)
    if not program:
        flash('指定された体験プログラムが見つかりません。', 'error')
        return redirect(url_for('reservation.index'))
    
    form = ReservationForm()
    # 体験プログラムの選択肢を設定
    form.program_id.choices = [(p.id, p.name) for p in ExperienceProgram.query.all()]
    form.program_id.data = program_id
    
    if form.validate_on_submit():
        try:
            # 定員チェック
            existing_reservations = Reservation.query.filter_by(
                program_id=program_id,
                reservation_date=form.reservation_date.data
            ).all()
            
            total_participants = sum(r.number_of_participants for r in existing_reservations)
            if total_participants + form.number_of_participants.data > program.capacity:
                flash(f'この日の予約が満席です。（残り: {program.capacity - total_participants}名）', 'error')
                return render_template('reservations/create.html', form=form, program=program)
            
            # 予約を作成
            reservation = Reservation(
                program_id=form.program_id.data,
                name=form.name.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                reservation_date=form.reservation_date.data,
                number_of_participants=form.number_of_participants.data
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            flash('予約が完了しました。', 'success')
            return redirect(url_for('reservation.show', id=reservation.id))
            
        except Exception as e:
            db.session.rollback()
            flash('予約の作成中にエラーが発生しました。', 'error')
    
    return render_template('reservations/create.html', form=form, program=program)


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
