# seed_enrollments.py
from HillSide import create_app
from HillSide.extensions import db
from HillSide.models import Enrollment, User, Course, StatusEnum
from random import choice, randint
from datetime import datetime, timedelta

# List of realistic cities/towns your students might be joining from
CITIES = [
    "Nairobi", "Lagos", "Accra", "Kampala", "Dar es Salaam", "Addis Ababa",
    "Johannesburg", "Cape Town", "Abidjan", "Dakar", "Kigali", "Lusaka",
    "Harare", "Mombasa", "Kumasi", "Ibadan", "Port Harcourt", "Enugu",
    "Kinshasa", "Bamako", "Ouagadougou", "Lomé", "Yaoundé", "Douala",
    "Cairo", "Casablanca", "Tunis", "Algiers", "Khartoum",
    "London", "Manchester", "Birmingham", "New York", "Toronto", "Sydney",
    "Mumbai", "Delhi", "Bangalore", "Lahore", "Karachi", "Dubai"
]

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

        for _ in range(num_enrollments):
            course = choice(courses)
            if course.id in chosen_courses:
                continue
            chosen_courses.add(course.id)

            status = choice(statuses)
            progress = 0.0
            if status == StatusEnum.ACTIVE:
                progress = round(randint(0, 95), 1)        # 0–95%
            elif status == StatusEnum.COMPLETED:
                progress = 100.0
            else:  # DROPPED
                progress = round(randint(5, 70), 1)

            enrollment = Enrollment(
                user_id=user.id,
                course_id=course.id,
                progress=progress,
                status=status.value,           # unchanged – you’re using native_enum=False
                city_town=choice(CITIES)       # NEW: random realistic city
            )
            enrollments.append(enrollment)

    db.session.bulk_save_objects(enrollments)
    db.session.commit()
    print(f"Created {len(enrollments)} random enrollments with city/town data!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_enrollments()