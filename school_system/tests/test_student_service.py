import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from school_system.services.student_service import StudentService

def test_student_service():
    """Test the student service functionality."""
    try:
        # Test student service
        service = StudentService()

        # Get all students
        students = service.get_all_students()
        print(f'Total students from service: {len(students)}')

        if students:
            print('First student:', students[0])
            print('Student attributes:')
            print('  student_id:', getattr(students[0], 'student_id', 'N/A'))
            print('  name:', getattr(students[0], 'name', 'N/A'))
            print('  stream:', getattr(students[0], 'stream', 'N/A'))
            print('  admission_number:', getattr(students[0], 'admission_number', 'N/A'))

        # Get all streams
        streams = service.get_all_streams()
        print(f'Available streams: {streams}')

        # Test filtering
        if streams:
            red_students = service.get_all_students(stream='4 Red')
            print(f'Students in 4 Red: {len(red_students)}')

            science_students = service.get_all_students(stream='Science')
            print(f'Students in Science: {len(science_students)}')

        print('Student service test completed successfully!')

    except Exception as e:
        print(f'Error testing student service: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_student_service()