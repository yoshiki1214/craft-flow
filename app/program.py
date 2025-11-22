"""
体験プログラム管理コントローラ

体験プログラムのCRUD機能を提供するBlueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from .models import ExperienceProgram, Reservation
from .forms import ExperienceProgramForm
from . import db

program_bp = Blueprint('program', __name__)


@program_bp.route('/')
def index():
    """体験プログラムの一覧を表示する"""
    programs = ExperienceProgram.query.order_by(ExperienceProgram.id).all()
    return render_template('programs/index.html', programs=programs)


@program_bp.route('/create', methods=['GET', 'POST'])
def create():
    """体験プログラムを作成する"""
    form = ExperienceProgramForm()
    
    if form.validate_on_submit():
        try:
            # プログラム名の重複チェック
            existing_program = ExperienceProgram.query.filter_by(name=form.name.data).first()
            if existing_program:
                flash('このプログラム名は既に登録されています。', 'error')
                return render_template('programs/create.html', form=form)
            
            program = ExperienceProgram(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                capacity=form.capacity.data
            )
            
            db.session.add(program)
            db.session.commit()
            
            flash('体験プログラムを登録しました。', 'success')
            return redirect(url_for('program.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'体験プログラムの登録中にエラーが発生しました: {str(e)[:100]}', 'error')
    
    return render_template('programs/create.html', form=form)


@program_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """体験プログラムを編集する"""
    program = db.session.get(ExperienceProgram, id)
    if not program:
        abort(404)
    
    form = ExperienceProgramForm(obj=program)
    
    if form.validate_on_submit():
        try:
            # プログラム名の重複チェック（自分自身を除く）
            existing_program = ExperienceProgram.query.filter(
                ExperienceProgram.name == form.name.data,
                ExperienceProgram.id != id
            ).first()
            if existing_program:
                flash('このプログラム名は既に登録されています。', 'error')
                return render_template('programs/edit.html', form=form, program=program)
            
            # プログラム情報を更新
            program.name = form.name.data
            program.description = form.description.data
            program.price = form.price.data
            program.capacity = form.capacity.data
            
            db.session.commit()
            
            flash('体験プログラムを更新しました。', 'success')
            return redirect(url_for('program.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'体験プログラムの更新中にエラーが発生しました: {str(e)[:100]}', 'error')
    
    return render_template('programs/edit.html', form=form, program=program)


@program_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """体験プログラムを削除する"""
    program = db.session.get(ExperienceProgram, id)
    if not program:
        abort(404)
    
    try:
        # 関連する予約があるかチェック
        reservations = Reservation.query.filter_by(program_id=id).count()
        if reservations > 0:
            flash(f'このプログラムには{reservations}件の予約が登録されているため、削除できません。', 'error')
            return redirect(url_for('program.index'))
        
        db.session.delete(program)
        db.session.commit()
        flash('体験プログラムを削除しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'体験プログラムの削除中にエラーが発生しました: {str(e)[:100]}', 'error')
    
    return redirect(url_for('program.index'))

