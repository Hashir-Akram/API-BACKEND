"""
SQLite database models and operations using SQLAlchemy.
Expanded to support broader API and UI testing scenarios.
"""
from __future__ import annotations

import json
from datetime import date, datetime

import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()


def _now():
    return datetime.utcnow()


def _normalize_tags(tags):
    if tags is None:
        return ""
    if isinstance(tags, str):
        values = [tag.strip() for tag in tags.split(",") if tag.strip()]
    else:
        values = [str(tag).strip() for tag in tags if str(tag).strip()]

    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return ",".join(unique_values)


def _parse_tags(raw_value):
    if not raw_value:
        return []
    return [tag for tag in raw_value.split(",") if tag]


def _paginate(query, page, per_page):
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return paginated.items, {
        "page": paginated.page,
        "per_page": paginated.per_page,
        "total": paginated.total,
        "pages": paginated.pages,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
    }


class User(db.Model):
    """User model for SQLite database."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    projects = db.relationship("Project", backref="owner", lazy=True, foreign_keys="Project.owner_id")
    created_tasks = db.relationship("Task", backref="creator", lazy=True, foreign_keys="Task.created_by")
    assigned_tasks = db.relationship("Task", backref="assignee", lazy=True, foreign_keys="Task.assigned_to")
    comments = db.relationship("Comment", backref="author", lazy=True, foreign_keys="Comment.author_id")
    audit_logs = db.relationship("AuditLog", backref="actor", lazy=True, foreign_keys="AuditLog.actor_id")

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(30), nullable=False, default="active", index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        tasks = list(self.tasks)
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "owner_id": self.owner_id,
            "owner_name": self.owner.name if self.owner else None,
            "task_count": len(tasks),
            "completed_task_count": len([task for task in tasks if task.status == "done"]),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(30), nullable=False, default="todo", index=True)
    priority = db.Column(db.String(30), nullable=False, default="medium", index=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    estimated_hours = db.Column(db.Float, nullable=True)
    tags = db.Column(db.String(255), nullable=False, default="")
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    comments = db.relationship("Comment", backref="task", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "tags": _parse_tags(self.tags),
            "project_id": self.project_id,
            "project_title": self.project.title if self.project else None,
            "created_by": self.created_by,
            "created_by_name": self.creator.name if self.creator else None,
            "assigned_to": self.assigned_to,
            "assigned_to_name": self.assignee.name if self.assignee else None,
            "comment_count": len(self.comments),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "author_id": self.author_id,
            "author_name": self.author.name if self.author else None,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    details = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, nullable=False, default=_now, index=True)

    def to_dict(self):
        try:
            parsed_details = json.loads(self.details or "{}")
        except json.JSONDecodeError:
            parsed_details = {"raw": self.details}

        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "actor_name": self.actor.name if self.actor else None,
            "details": parsed_details,
            "created_at": self.created_at.isoformat(),
        }


class UserStore:
    @staticmethod
    def create_user(user_data):
        try:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                age=user_data["age"],
                role=user_data.get("role", "user"),
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def get_user_by_id(user_id):
        user = db.session.get(User, user_id)
        return user.to_dict() if user else None

    @staticmethod
    def get_user_object_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user.to_dict() if user else None

    @staticmethod
    def get_user_object_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users():
        users = User.query.order_by(User.created_at.desc()).all()
        return [user.to_dict() for user in users]

    @staticmethod
    def list_users(filters):
        query = User.query

        role = filters.get("role")
        search = filters.get("q")
        if role:
            query = query.filter(User.role == role)
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

        sort_map = {
            "name": User.name,
            "email": User.email,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
            "age": User.age,
        }
        sort_column = sort_map.get(filters.get("sort_by", "created_at"), User.created_at)
        if filters.get("sort_order") == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items, pagination = _paginate(query, filters["page"], filters["per_page"])
        return [item.to_dict() for item in items], pagination

    @staticmethod
    def update_user(user_id, user_data):
        user = db.session.get(User, user_id)
        if not user:
            return None

        try:
            if "name" in user_data:
                user.name = user_data["name"]
            if "email" in user_data:
                user.email = user_data["email"]
            if "age" in user_data:
                user.age = user_data["age"]
            if "role" in user_data:
                user.role = user_data["role"]
            if "password" in user_data:
                user.set_password(user_data["password"])

            user.updated_at = _now()
            db.session.commit()
            return user.to_dict()
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def delete_user(user_id):
        user = db.session.get(User, user_id)
        if not user:
            return None

        user_dict = user.to_dict()
        db.session.delete(user)
        db.session.commit()
        return user_dict

    @staticmethod
    def email_exists(email, exclude_user_id=None):
        query = User.query.filter_by(email=email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    @staticmethod
    def reset():
        try:
            Comment.query.delete()
            Task.query.delete()
            Project.query.delete()
            AuditLog.query.delete()
            User.query.delete()
            db.session.commit()

            try:
                for table_name in ["comments", "tasks", "projects", "audit_logs", "users"]:
                    db.session.execute(db.text(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"))
                db.session.commit()
            except Exception:
                db.session.rollback()

            UserStore._init_sample_data()
        except Exception as exc:
            db.session.rollback()
            raise exc

    @staticmethod
    def _init_sample_data():
        admin = User(name="Admin User", email="admin@example.com", age=30, role="admin")
        admin.set_password("Admin@123")
        john = User(name="John Doe", email="john@example.com", age=25, role="user")
        john.set_password("User@123")
        sara = User(name="Sara Tester", email="sara@example.com", age=28, role="user")
        sara.set_password("Tester@123")

        db.session.add_all([admin, john, sara])
        db.session.commit()

        website = Project(
            title="Website Redesign",
            description="Revamp the marketing website and improve conversion funnel pages.",
            status="active",
            owner_id=admin.id,
        )
        automation = Project(
            title="API Automation Suite",
            description="Build smoke, regression, and contract coverage for the public API.",
            status="active",
            owner_id=john.id,
        )
        mobile = Project(
            title="Mobile Release 2.1",
            description="Prepare backlog, fixes, and QA sign-off for the next mobile release.",
            status="on_hold",
            owner_id=sara.id,
        )

        db.session.add_all([website, automation, mobile])
        db.session.commit()

        tasks = [
            Task(
                title="Create landing page wireframes",
                description="Initial design concepts for hero, pricing, and signup sections.",
                status="in_progress",
                priority="high",
                due_date=date.fromisoformat("2026-03-20"),
                estimated_hours=12,
                tags=_normalize_tags(["design", "ux"]),
                project_id=website.id,
                created_by=admin.id,
                assigned_to=sara.id,
            ),
            Task(
                title="Implement authentication regression suite",
                description="Cover login, invalid credentials, lockout, and token-expiry cases.",
                status="todo",
                priority="critical",
                due_date=date.fromisoformat("2026-03-18"),
                estimated_hours=10,
                tags=_normalize_tags(["api", "automation", "auth"]),
                project_id=automation.id,
                created_by=admin.id,
                assigned_to=john.id,
            ),
            Task(
                title="Stabilize payment callbacks",
                description="Investigate intermittent callback failures in staging.",
                status="blocked",
                priority="critical",
                due_date=date.fromisoformat("2026-03-16"),
                estimated_hours=8,
                tags=_normalize_tags(["backend", "payments"]),
                project_id=mobile.id,
                created_by=sara.id,
                assigned_to=admin.id,
            ),
            Task(
                title="Write negative API test cases",
                description="Add validation, auth, and permission edge cases.",
                status="done",
                priority="medium",
                due_date=date.fromisoformat("2026-03-10"),
                estimated_hours=6,
                tags=_normalize_tags(["negative", "api"]),
                project_id=automation.id,
                created_by=john.id,
                assigned_to=sara.id,
            ),
        ]
        db.session.add_all(tasks)
        db.session.commit()

        comments = [
            Comment(task_id=tasks[0].id, author_id=admin.id, content="Make sure the mobile version gets separate CTA variants."),
            Comment(task_id=tasks[1].id, author_id=john.id, content="I will start with the happy path and expired token cases."),
            Comment(task_id=tasks[2].id, author_id=sara.id, content="Blocked pending logs from the payments team."),
        ]
        db.session.add_all(comments)
        db.session.commit()

        logs = [
            AuditLog(entity_type="project", entity_id=website.id, action="seeded", actor_id=admin.id, details=json.dumps({"title": website.title})),
            AuditLog(entity_type="task", entity_id=tasks[1].id, action="seeded", actor_id=admin.id, details=json.dumps({"title": tasks[1].title})),
        ]
        db.session.add_all(logs)
        db.session.commit()


class ProjectStore:
    @staticmethod
    def create_project(project_data):
        project = Project(**project_data)
        db.session.add(project)
        db.session.commit()
        return project.to_dict()

    @staticmethod
    def get_project_object(project_id):
        return db.session.get(Project, project_id)

    @staticmethod
    def get_project_by_id(project_id):
        project = db.session.get(Project, project_id)
        return project.to_dict() if project else None

    @staticmethod
    def list_projects(filters):
        query = Project.query
        if filters.get("status"):
            query = query.filter(Project.status == filters["status"])
        if filters.get("owner_id"):
            query = query.filter(Project.owner_id == filters["owner_id"])
        if filters.get("q"):
            pattern = f"%{filters['q']}%"
            query = query.filter(or_(Project.title.ilike(pattern), Project.description.ilike(pattern)))

        sort_map = {
            "title": Project.title,
            "status": Project.status,
            "created_at": Project.created_at,
            "updated_at": Project.updated_at,
        }
        sort_column = sort_map.get(filters.get("sort_by", "updated_at"), Project.updated_at)
        if filters.get("sort_order") == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items, pagination = _paginate(query, filters["page"], filters["per_page"])
        return [project.to_dict() for project in items], pagination

    @staticmethod
    def update_project(project, project_data):
        for key, value in project_data.items():
            setattr(project, key, value)
        project.updated_at = _now()
        db.session.commit()
        return project.to_dict()

    @staticmethod
    def delete_project(project):
        project_dict = project.to_dict()
        db.session.delete(project)
        db.session.commit()
        return project_dict


class TaskStore:
    @staticmethod
    def create_task(task_data):
        if "tags" in task_data:
            task_data = {**task_data, "tags": _normalize_tags(task_data["tags"])}
        task = Task(**task_data)
        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    @staticmethod
    def get_task_object(task_id):
        return db.session.get(Task, task_id)

    @staticmethod
    def get_task_by_id(task_id):
        task = db.session.get(Task, task_id)
        return task.to_dict() if task else None

    @staticmethod
    def list_tasks(filters):
        query = Task.query

        if filters.get("project_id"):
            query = query.filter(Task.project_id == filters["project_id"])
        if filters.get("status"):
            query = query.filter(Task.status == filters["status"])
        if filters.get("priority"):
            query = query.filter(Task.priority == filters["priority"])
        if filters.get("assigned_to"):
            query = query.filter(Task.assigned_to == filters["assigned_to"])
        if filters.get("created_by"):
            query = query.filter(Task.created_by == filters["created_by"])
        if filters.get("q"):
            pattern = f"%{filters['q']}%"
            query = query.filter(or_(Task.title.ilike(pattern), Task.description.ilike(pattern), Task.tags.ilike(pattern)))
        if filters.get("overdue"):
            query = query.filter(Task.due_date < date.today(), Task.status != "done")

        sort_map = {
            "title": Task.title,
            "status": Task.status,
            "priority": Task.priority,
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "due_date": Task.due_date,
        }
        sort_column = sort_map.get(filters.get("sort_by", "updated_at"), Task.updated_at)
        if filters.get("sort_order") == "asc":
            query = query.order_by(sort_column.asc().nullslast())
        else:
            query = query.order_by(sort_column.desc().nullslast())

        items, pagination = _paginate(query, filters["page"], filters["per_page"])
        return [task.to_dict() for task in items], pagination

    @staticmethod
    def update_task(task, task_data):
        for key, value in task_data.items():
            if key == "tags":
                task.tags = _normalize_tags(value)
            else:
                setattr(task, key, value)
        task.updated_at = _now()
        db.session.commit()
        return task.to_dict()

    @staticmethod
    def delete_task(task):
        task_dict = task.to_dict()
        db.session.delete(task)
        db.session.commit()
        return task_dict


class CommentStore:
    @staticmethod
    def list_comments(task_id):
        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.asc()).all()
        return [comment.to_dict() for comment in comments]

    @staticmethod
    def create_comment(comment_data):
        comment = Comment(**comment_data)
        db.session.add(comment)
        db.session.commit()
        return comment.to_dict()

    @staticmethod
    def get_comment_object(comment_id):
        return db.session.get(Comment, comment_id)

    @staticmethod
    def delete_comment(comment):
        comment_dict = comment.to_dict()
        db.session.delete(comment)
        db.session.commit()
        return comment_dict


class AuditLogStore:
    @staticmethod
    def create_log(entity_type, action, actor_id=None, entity_id=None, details=None):
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            details=json.dumps(details or {}),
        )
        db.session.add(log)
        db.session.commit()
        return log.to_dict()

    @staticmethod
    def list_logs(filters):
        query = AuditLog.query
        if filters.get("entity_type"):
            query = query.filter(AuditLog.entity_type == filters["entity_type"])
        if filters.get("action"):
            query = query.filter(AuditLog.action == filters["action"])
        if filters.get("actor_id"):
            query = query.filter(AuditLog.actor_id == filters["actor_id"])

        query = query.order_by(AuditLog.created_at.desc())
        items, pagination = _paginate(query, filters["page"], filters["per_page"])
        return [log.to_dict() for log in items], pagination


def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            UserStore._init_sample_data()
