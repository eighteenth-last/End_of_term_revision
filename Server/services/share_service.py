"""
共享服务模块
提供科目共享的核心业务逻辑和权限控制
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database.models import Subject, SubjectShare, ShareType, User
from typing import List, Optional, Dict, Any
from fastapi import HTTPException


class ShareService:
    """共享服务类"""
    
    @staticmethod
    def can_access_subject(user_id: int, subject_id: int, db: Session) -> bool:
        """
        判断用户是否有权访问科目（查看和练习）
        
        Args:
            user_id: 用户ID
            subject_id: 科目ID
            db: 数据库会话
            
        Returns:
            bool: 是否有访问权限
        """
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return False
        
        # 1. 如果是科目拥有者，直接允许
        if subject.user_id == user_id:
            return True
        
        # 2. 检查是否有共享权限
        share = db.query(SubjectShare).filter(
            SubjectShare.subject_id == subject_id,
            or_(
                # 指定用户共享
                and_(
                    SubjectShare.share_type == ShareType.USER,
                    SubjectShare.target_user_id == user_id
                ),
                # 公共共享
                SubjectShare.share_type == ShareType.PUBLIC
            )
        ).first()
        
        return share is not None
    
    @staticmethod
    def can_edit_subject(user_id: int, subject_id: int, db: Session) -> bool:
        """
        判断用户是否有权编辑科目（仅拥有者可以）
        
        Args:
            user_id: 用户ID
            subject_id: 科目ID
            db: 数据库会话
            
        Returns:
            bool: 是否有编辑权限
        """
        subject = db.query(Subject).filter(
            Subject.id == subject_id,
            Subject.user_id == user_id
        ).first()
        
        return subject is not None
    
    @staticmethod
    def get_accessible_subjects(user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        获取用户可访问的所有科目（自己的 + 共享的）
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            List[Dict]: 科目列表，包含额外的共享信息
        """
        result = []
        
        # 1. 获取自己创建的科目
        own_subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
        for subject in own_subjects:
            # 检查该科目是否已被共享出去
            has_shared = db.query(SubjectShare).filter(
                SubjectShare.subject_id == subject.id
            ).first() is not None
            
            result.append({
                'id': subject.id,
                'name': subject.name,
                'user_id': subject.user_id,
                'created_at': subject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_owner': True,
                'is_shared': False,
                'owner_username': None,
                'share_type': None,
                'has_shared': has_shared  # 新增：是否已共享出去
            })
        
        # 2. 获取共享给自己的科目（指定用户共享）
        user_shares = db.query(SubjectShare, Subject, User).join(
            Subject, SubjectShare.subject_id == Subject.id
        ).join(
            User, Subject.user_id == User.id
        ).filter(
            SubjectShare.target_user_id == user_id,
            SubjectShare.share_type == ShareType.USER
        ).all()
        
        for share, subject, owner in user_shares:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'user_id': subject.user_id,
                'created_at': subject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_owner': False,
                'is_shared': True,
                'owner_username': owner.username,
                'share_type': 'USER',
                'has_shared': False  # 非拥有者，此字段无意义
            })
        
        # 3. 获取公共科目（排除自己创建的）
        public_shares = db.query(SubjectShare, Subject, User).join(
            Subject, SubjectShare.subject_id == Subject.id
        ).join(
            User, Subject.user_id == User.id
        ).filter(
            SubjectShare.share_type == ShareType.PUBLIC,
            Subject.user_id != user_id  # 排除自己的科目
        ).all()
        
        for share, subject, owner in public_shares:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'user_id': subject.user_id,
                'created_at': subject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_owner': False,
                'is_shared': True,
                'owner_username': owner.username,
                'share_type': 'PUBLIC',
                'has_shared': False  # 非拥有者，此字段无意义
            })
        
        return result
        
        # 2. 获取共享给自己的科目（指定用户共享）
        user_shares = db.query(SubjectShare, Subject, User).join(
            Subject, SubjectShare.subject_id == Subject.id
        ).join(
            User, Subject.user_id == User.id
        ).filter(
            SubjectShare.target_user_id == user_id,
            SubjectShare.share_type == ShareType.USER
        ).all()
        
        for share, subject, owner in user_shares:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'user_id': subject.user_id,
                'created_at': subject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_owner': False,
                'is_shared': True,
                'owner_username': owner.username,
                'share_type': 'USER'
            })
        
        # 3. 获取公共科目（排除自己创建的）
        public_shares = db.query(SubjectShare, Subject, User).join(
            Subject, SubjectShare.subject_id == Subject.id
        ).join(
            User, Subject.user_id == User.id
        ).filter(
            SubjectShare.share_type == ShareType.PUBLIC,
            Subject.user_id != user_id  # 排除自己的科目
        ).all()
        
        for share, subject, owner in public_shares:
            result.append({
                'id': subject.id,
                'name': subject.name,
                'user_id': subject.user_id,
                'created_at': subject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_owner': False,
                'is_shared': True,
                'owner_username': owner.username,
                'share_type': 'PUBLIC'
            })
        
        return result
    
    @staticmethod
    def set_share(
        owner_user_id: int,
        subject_id: int,
        target_user_id: Optional[int],
        share_type: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        设置科目共享
        
        Args:
            owner_user_id: 科目拥有者ID
            subject_id: 科目ID
            target_user_id: 目标用户ID（公共共享时为None）
            share_type: 共享类型（USER/PUBLIC）
            db: 数据库会话
            
        Returns:
            Dict: 共享记录信息
        """
        # 验证权限
        if not ShareService.can_edit_subject(owner_user_id, subject_id, db):
            raise HTTPException(status_code=403, detail="无权共享此科目")
        
        # 验证共享类型
        if share_type not in ['USER', 'PUBLIC']:
            raise HTTPException(status_code=400, detail="无效的共享类型")
        
        # 验证参数
        if share_type == 'USER' and not target_user_id:
            raise HTTPException(status_code=400, detail="指定用户共享必须提供目标用户ID")
        
        if share_type == 'PUBLIC':
            target_user_id = None
        
        # 检查是否已存在相同的共享记录
        existing_share = db.query(SubjectShare).filter(
            SubjectShare.subject_id == subject_id,
            SubjectShare.target_user_id == target_user_id,
            SubjectShare.share_type == ShareType[share_type]
        ).first()
        
        if existing_share:
            raise HTTPException(status_code=400, detail="该共享配置已存在")
        
        # 创建共享记录
        share = SubjectShare(
            owner_user_id=owner_user_id,
            subject_id=subject_id,
            target_user_id=target_user_id,
            share_type=ShareType[share_type]
        )
        
        db.add(share)
        db.commit()
        db.refresh(share)
        
        return {
            'id': share.id,
            'subject_id': share.subject_id,
            'target_user_id': share.target_user_id,
            'share_type': share.share_type.value,
            'created_at': share.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def cancel_share(
        owner_user_id: int,
        subject_id: int,
        target_user_id: Optional[int],
        share_type: Optional[str],
        db: Session
    ) -> Dict[str, str]:
        """
        取消科目共享
        
        Args:
            owner_user_id: 科目拥有者ID
            subject_id: 科目ID
            target_user_id: 目标用户ID
            share_type: 共享类型
            db: 数据库会话
            
        Returns:
            Dict: 操作结果
        """
        # 验证权限
        if not ShareService.can_edit_subject(owner_user_id, subject_id, db):
            raise HTTPException(status_code=403, detail="无权操作此科目")
        
        # 构建查询条件
        query = db.query(SubjectShare).filter(
            SubjectShare.subject_id == subject_id,
            SubjectShare.owner_user_id == owner_user_id
        )
        
        if target_user_id is not None:
            query = query.filter(SubjectShare.target_user_id == target_user_id)
        
        if share_type:
            query = query.filter(SubjectShare.share_type == ShareType[share_type])
        
        share = query.first()
        
        if not share:
            raise HTTPException(status_code=404, detail="共享记录不存在")
        
        db.delete(share)
        db.commit()
        
        return {"message": "共享已取消"}
    
    @staticmethod
    def get_share_status(subject_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        获取科目的共享状态列表
        
        Args:
            subject_id: 科目ID
            db: 数据库会话
            
        Returns:
            List[Dict]: 共享状态列表
        """
        shares = db.query(SubjectShare, User).outerjoin(
            User, SubjectShare.target_user_id == User.id
        ).filter(
            SubjectShare.subject_id == subject_id
        ).all()
        
        result = []
        for share, user in shares:
            result.append({
                'id': share.id,
                'subject_id': share.subject_id,
                'target_user_id': share.target_user_id,
                'target_username': user.username if user else None,
                'share_type': share.share_type.value,
                'created_at': share.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return result
    
    @staticmethod
    def get_my_shared_subjects(user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        获取我共享出去的科目列表
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            List[Dict]: 共享科目列表
        """
        shares = db.query(SubjectShare, Subject).join(
            Subject, SubjectShare.subject_id == Subject.id
        ).filter(
            SubjectShare.owner_user_id == user_id
        ).all()
        
        result = []
        for share, subject in shares:
            result.append({
                'id': share.id,
                'subject_id': subject.id,
                'subject_name': subject.name,
                'target_user_id': share.target_user_id,
                'share_type': share.share_type.value,
                'created_at': share.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return result
