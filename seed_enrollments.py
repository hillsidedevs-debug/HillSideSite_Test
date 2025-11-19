from HillSide import create_app
from HillSide.extensions import db
from HillSide.models import Enrollment, User, Course, StatusEnum
from random import choice, randint
from datetime import datetime, timedelta

def seed_enrollments(n=100):
    users = User.query.all()
    courses = Course.query.all()

    if not users or not courses:
        print("Make sure you have users and courses in the DB first!")
        return
    
    enrollments = []
    statuses = [StatusEnum.ACTIVE, StatusEnum.COMPLETED, StatusEnum.DROPPED]

    for user in users:
        num_enrollments = randint(0, 15)
        chosen_courses = set()

        for i in range(num_enrollments):
            course = choice(courses)
            if course.id in chosen_courses:
                continue
            chosen_courses.add(course.id)

            status = choice(statuses)
            progress = 0.0
            if status == StatusEnum.ACTIVE:
                progress = round(randint(0, 95), 1)  # 0–95%
            elif status == StatusEnum.COMPLETED:
                progress = 100.0
            else:  # DROPPED
                progress = round(randint(5, 70), 1)

            enrollment = Enrollment(
                user_id=user.id,
                course_id=course.id,
                progress=progress,
                status=status.value  # because we use PyEnum with native_enum=False
            )
            enrollments.append(enrollment)
    db.session.bulk_save_objects(enrollments)
    db.session.commit()
    print(f"Created {len(enrollments)} random enrollments!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_enrollments()
