from django.db import migrations


ADMIN_PASSWORD = (
    'pbkdf2_sha256$1200000$COCdEOe49FuZ7TU7JYrpH8$'
    'xJWId5QuFwVs+2R9t2lYNs4d7nCSuhaGXL4BixrhROo='
)
STUDENT_PASSWORD = (
    'pbkdf2_sha256$1200000$Ld0mzzqwziohOQBEC2INMg$'
    'DdL0Z6/dK0q2TEPYDQOAGXzPpeEa+3sXwiSo2Vr1oQc='
)


def create_default_data(apps, schema_editor):
    user_model = apps.get_model('auth', 'User')
    course_model = apps.get_model('api', 'Course')

    admin_user, created = user_model.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'password': ADMIN_PASSWORD,
            'email': '',
        },
    )
    if not created:
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.password = ADMIN_PASSWORD
        admin_user.save(
            update_fields=['is_staff', 'is_superuser', 'is_active', 'password']
        )

    student_user, created = user_model.objects.get_or_create(
        username='student',
        defaults={
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'password': STUDENT_PASSWORD,
            'email': '',
        },
    )
    if not created:
        student_user.is_staff = False
        student_user.is_superuser = False
        student_user.is_active = True
        student_user.password = STUDENT_PASSWORD
        student_user.save(
            update_fields=['is_staff', 'is_superuser', 'is_active', 'password']
        )

    for title, description in [
        ('Angular Basics', 'Grundlagen fuer die Frontend-Entwicklung'),
        ('TypeScript', 'Typen, Interfaces und saubere Strukturen'),
        ('Oracle SQL', 'Arbeiten mit Oracle und SQL-Grundlagen'),
    ]:
        course_model.objects.get_or_create(
            title=title,
            defaults={'description': description, 'created_by': admin_user},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_data, noop_reverse),
    ]
