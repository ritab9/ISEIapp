from django.core.management.base import BaseCommand
from reporting.models import Subject, SubjectCategory


class Command(BaseCommand):
    """Django command to populate Subjects."""

    help = 'Create default Subjects.'

    def handle(self, *args, **kwargs):
        subjects_by_category = {
            SubjectCategory.WELLNESS_HEALTH_PE: ['Health/Mental Health', 'Mental Health', 'Massage',
                                                 'Physical Education', 'Outdoor Educ Classes'],
            SubjectCategory.SCIENCE: ['Biology', 'Chemistry', 'Physics', 'Anatomy/Physiology',
                                      'Advanced Anatomy/Physiology', 'Physical Science/Geoscience'],
            SubjectCategory.LANGUAGE_ARTS: ['English I-IV', 'Public Speaking', 'ASL'],
            SubjectCategory.MODERN_LANGUAGE: ['Communication', 'Spanish', 'French', 'Romanian', 'Hungarian'],
            SubjectCategory.MATH: ['Remedial/Pre-Algebra', 'Algebra I, II', 'Geometry', 'Consumer Math', 'Pre-Algebra',
                                   'Pre-Calculus', 'Math Models', 'College Prep Math', 'Statistics',
                                   'Elem/Middle School Math'],
            SubjectCategory.BIBLE: ['Bible I-IV'],
            SubjectCategory.SOCIAL_STUDIES: ['Economics', 'Government', 'World History', 'US History',
                                             'Personal Finance', 'Business', 'Geography'],
            SubjectCategory.COMPUTER_TECH: ['Keyboarding/Computer Apps'],
            SubjectCategory.FINE_ARTS: ['Choir/Chorale', 'Bell Choir', 'Orchestra/Band/Strings', 'Voice/Piano Lessons',
                                        'Music Theory', 'Art/Creative Drawing', 'Digital Photography'],
            SubjectCategory.VOCATIONAL_ARTS_COURSES: ['Agriculture/Gardening/Farm', 'Life Skills',
                                                      'Auto Mechanics/small engines', 'Wood Working', 'Flight',
                                                      'Welding', 'First Aid & CPR', 'Small engines', 'Canvassing',
                                                      'Vocational Ethics', 'Radio Broadcasting',
                                                      'Maintenance/Plant Services']
        }

        for category, subjects in subjects_by_category.items():
            for subject_name in subjects:
                Subject.objects.get_or_create(name=subject_name, category=category)

        self.stdout.write(self.style.SUCCESS('Subjects populated successfully.'))
