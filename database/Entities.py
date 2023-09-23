from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define association table for many-to-many relationship between Course and Category
course_category = db.Table('course_category',
                           db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
                           db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                           )


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    email = db.Column(db.String(45))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    createdAt = db.Column(db.DateTime)
    credits = db.Column(db.String(255))
    deactivation_date = db.Column(db.DateTime)
    language = db.Column(db.String(25))
    updatedAt = db.Column(db.String(255))
    level = db.Column(db.Integer)
    points = db.Column(db.Integer)
    restrict_email = db.Column(db.String(255))
    status = db.Column(db.String(25))
    timezone = db.Column(db.String(45))
    user_type = db.Column(db.String(255))

    # Define bidirectional relationships with backref
    badges = db.relationship("Badge", backref="user_badges", cascade="all, delete-orphan")
    user_certifications = db.relationship("Certification", backref="certified_user", cascade="all, delete-orphan")
    # groups = db.relationship("Group", backref="user", cascade="all, delete-orphan")
    groups = db.relationship("Group", backref="group_user", cascade="all, delete-orphan")
    quizzes = db.relationship("QuizzUser", backref="user_quizzes", cascade="all, delete-orphan")
    surveys = db.relationship("SurveyUser", backref="user_surveys", cascade="all, delete-orphan")
    # user_badges = db.relationship("UserBadge", backref="user")
    user_badges = db.relationship("UserBadge", backref="user_badge")
    user_courses = db.relationship("UserCourse")


class Badge(db.Model):
    __tablename__ = 'badge'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    badge_set_id = db.Column(db.String(255))
    criteria = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    issued_on = db.Column(db.String(255))
    issued_on_timestamp = db.Column(db.String(255))
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))

    # Define bidirectional relationships with backref
    user = db.relationship("User", backref="user_badge")


class Branch(db.Model):
    __tablename__ = 'branch'

    Branch_id = db.Column(db.Integer, primary_key=True)
    Branch_name = db.Column(db.String(100))
    Branch_description = db.Column(db.String(100))
    property = db.Column(db.String(45))


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    parent_category_id = db.Column(db.Integer)
    price = db.Column(db.DECIMAL(10, 2))

    courses = db.relationship("Course", secondary=course_category, back_populates="categories")


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    big_avatar = db.Column(db.String(255))
    course_code = db.Column(db.String(10))
    creation_date = db.Column(db.DateTime)
    creator_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    expiration_datetime = db.Column(db.String(255))
    hide_from_catalog = db.Column(db.String(255))
    last_update_on = db.Column(db.String(255))
    level = db.Column(db.String(25))
    price = db.Column(db.DECIMAL(10, 2))
    shared = db.Column(db.String(255))
    shared_url = db.Column(db.String(255))
    start_datetime = db.Column(db.DateTime)
    status = db.Column(db.String(25))
    time_limit = db.Column(db.DateTime)

    # groups = db.relationship("GroupCourse", backref="course")
    groups = db.relationship("GroupCourse", backref="course_group")
    categories = db.relationship("Category", secondary=course_category, back_populates="courses")
    user_courses = db.relationship("UserCourse", back_populates="course")


class Certification(db.Model):
    __tablename__ = 'certification'

    id = db.Column(db.String(500), primary_key=True)
    course_name = db.Column(db.String(500))
    download_url = db.Column(db.String(500))
    expiration_date = db.Column(db.DateTime)
    expiration_date_timestamp = db.Column(db.DateTime)
    issued_date = db.Column(db.DateTime)
    public_url = db.Column(db.String(255))
    unique_id = db.Column(db.String(255))
    Course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    # user = db.relationship("User", backref="user_certifications")
    user = db.relationship("User", backref="certification_user")


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    belongs_to_branch = db.Column(db.Integer)
    price = db.Column(db.DECIMAL(10, 2))
    key_column = db.Column(db.String(255))
    max_redemptions = db.Column(db.Integer)
    redemptions_sofar = db.Column(db.Integer)
    branch_Branch_id = db.Column(db.Integer, db.ForeignKey('branch.Branch_id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("User", backref="user_groups")
    groups = db.relationship("GroupCourse", backref="group_courses")
    # redemptions = db.relationship("GroupRedemption", backref="group")
    redemptions = db.relationship("GroupRedemption", backref="group_redemptions")


class GroupCourse(db.Model):
    __tablename__ = 'group_has_course'

    Group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True, nullable=True)
    Course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True, nullable=True)

    group = db.relationship("Group", backref="courses")
    # course = db.relationship("Course", backref="groups")
    course = db.relationship("Course", backref="group_course")


class GroupRedemption(db.Model):
    __tablename__ = 'group_redemption'

    id = db.Column(db.Integer, primary_key=True)
    Group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    key_column = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)

    # group = db.relationship("Group", backref="redemptions")
    group = db.relationship("Group", backref="redemption_group")


class Quizz(db.Model):
    __tablename__ = 'quizz'

    quizz_id = db.Column(db.Integer, primary_key=True)
    quizz_name = db.Column(db.String(500), unique=True)
    createdAt = db.Column(db.DateTime)

    # users = db.relationship("QuizzUser", backref="quizz")
    users = db.relationship("QuizzUser", backref="quizz_users")


class QuizzUser(db.Model):
    __tablename__ = 'quizz_has_user'

    quizz_name = db.Column(db.String(500), db.ForeignKey('quizz.quizz_name'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    score = db.Column(db.Integer)
    status = db.Column(db.String(100))
    total_max = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    user = db.relationship("User", backref="user_quizz")
    quizz = db.relationship("Quizz", backref="quizz_association")


class Survey(db.Model):
    __tablename__ = 'survey'

    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime)
    completedAt = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    users = db.relationship("SurveyUser", backref="survey")


class SurveyUser(db.Model):
    __tablename__ = 'survey_has_user'

    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    score = db.Column(db.Integer)
    status = db.Column(db.String(100))

    user = db.relationship("User", backref="user_survey")
    # user = db.relationship("User", backref="surveys")


class UserBadge(db.Model):
    __tablename__ = 'user_has_badge'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), primary_key=True)

    user = db.relationship("User", backref="user_association")
    badge = db.relationship("Badge", backref="user_badge")


class UserCourse(db.Model):
    __tablename__ = 'user_has_course'

    User_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    Course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)

    course = db.relationship("Course", back_populates="user_courses")
    user = db.relationship("User", back_populates="user_courses")
