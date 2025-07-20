from mysql.connector import Error
from werkzeug.security import generate_password_hash

def get_user_by_email(db, email):
    db.execute('SELECT * FROM users WHERE Email = %s', (email,))
    return db.fetchone()

def get_all_departments(db):
    db.execute('SELECT * FROM department')
    return db.fetchall()

def create_user(db, user_data):
    hashed_password = generate_password_hash(user_data['password'])
    db.execute('''
        INSERT INTO users (ID, UserName, PasswordHash, FirstName, LastName, Email, Role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        user_data['ID'], user_data['username'], hashed_password, 
        user_data['firstname'], user_data['lastname'], user_data['email'], user_data['role']
    ))

def create_student(db, student_data):
    db.execute('''
        INSERT INTO student (ID, RegistrationNo, Phone, Class, DOB, Semester, DepartmentID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        student_data['ID'], student_data['registration_no'], student_data['phone'],
        student_data['class'], student_data['dob'], student_data['semester'], student_data['department_id']
    ))

def create_faculty(db, faculty_data):
    db.execute('''
        INSERT INTO faculty (ID, FacultyID, Phone, Qualification, `Level`, DepartmentID)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        faculty_data['ID'], faculty_data['faculty_id'], faculty_data['phone'],
        faculty_data['qualification'], faculty_data['level'], faculty_data['department_id']
    ))

def get_admin_dashboard_stats(db):
    db.execute('SELECT COUNT(*) as count FROM student')
    students_count = db.fetchone()['count']
    db.execute('SELECT COUNT(*) as count FROM faculty')
    faculty_count = db.fetchone()['count']
    db.execute('SELECT COUNT(*) as count FROM courses')
    courses_count = db.fetchone()['count']
    return {
        'students_count': students_count,
        'faculty_count': faculty_count,
        'courses_count': courses_count
    }

def get_faculty_dashboard_data(db, faculty_id):
    db.execute('''
        SELECT COUNT(*) as count 
        FROM courses 
        WHERE FacultyID = %s
    ''', (faculty_id,))
    courses_count = db.fetchone()['count']
    
    db.execute('''
        SELECT COUNT(DISTINCT StudentID) as count 
        FROM enrollment e
        JOIN courses c ON e.CourseID = c.CourseID
        WHERE c.FacultyID = %s
    ''', (faculty_id,))
    students_count = db.fetchone()['count']
    
    db.execute('''
        SELECT COUNT(*) as count 
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        WHERE c.FacultyID = %s AND cc.IsAssignment = 1
    ''', (faculty_id,))
    assignments_count = db.fetchone()['count']
    
    return {
        'courses_count': courses_count,
        'students_count': students_count,
        'assignments_count': assignments_count
    }

def get_student_dashboard_data(db, student_id):
    db.execute('''
        SELECT s.*, d.DepartmentName 
        FROM student s
        JOIN department d ON s.DepartmentID = d.DepartmentID
        WHERE s.ID = %s
    ''', (student_id,))
    student = db.fetchone()
    
    db.execute('''
        SELECT 
            c.CourseID, c.CourseName, c.CourseCredit,
            COALESCE(AVG(CAST(a.Attendance as FLOAT)) * 100, 0) as attendance_percentage,
            COUNT(DISTINCT cc.CourseContentID) as total_assignments,
            COUNT(DISTINCT s.SubmissionID) as completed_assignments
        FROM enrollment e
        JOIN courses c ON e.CourseID = c.CourseID
        LEFT JOIN attendance a ON e.CourseID = a.CourseID AND e.StudentID = a.StudentID
        LEFT JOIN coursecontent cc ON c.CourseID = cc.CourseID AND cc.IsAssignment = 1
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID AND s.StudentID = e.StudentID
        WHERE e.StudentID = %s
        GROUP BY c.CourseID, c.CourseName, c.CourseCredit
    ''', (student_id,))
    enrolled_courses = db.fetchall()
    
    db.execute('''
        SELECT cc.CCName, c.CourseName, cc.DueDate
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        JOIN enrollment e ON c.CourseID = e.CourseID
        WHERE e.StudentID = %s AND cc.IsAssignment = 1 AND cc.DueDate > NOW()
        ORDER BY cc.DueDate ASC
        LIMIT 5
    ''', (student_id,))
    recent_assignments = db.fetchall()
    
    return {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'recent_assignments': recent_assignments
    }

def get_course_details(db, course_id):
    db.execute('''
        SELECT c.*, f.ID as FacultyID, u.FirstName, u.LastName
        FROM courses c
        JOIN faculty f ON c.FacultyID = f.FacultyID
        JOIN users u ON f.ID = u.ID
        WHERE c.CourseID = %s
    ''', (course_id,))
    return db.fetchone()

def get_course_content(db, course_id):
    db.execute('SELECT * FROM coursecontent WHERE CourseID = %s', (course_id,))
    return db.fetchall()

def add_course_content(db, content_data):
    db.execute('''
        INSERT INTO coursecontent (CCName, Description, FileUrl, IsAssignment, CourseID, UserID)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        content_data['content_name'], content_data['description'], content_data['file_url'],
        content_data['is_assignment'], content_data['course_id'], content_data['user_id']
    ))

def get_all_users_with_details(db):
    db.execute('''
        SELECT u.ID, u.UserName, u.FirstName, u.LastName, u.Email, u.Role, 
               d.DepartmentName, 
               CASE 
                   WHEN u.Role = 'student' THEN s.RegistrationNo
                   WHEN u.Role = 'faculty' THEN f.FacultyID
               END as specific_id
        FROM users u
        LEFT JOIN student s ON u.ID = s.ID
        LEFT JOIN faculty f ON u.ID = f.ID
        LEFT JOIN department d ON (s.DepartmentID = d.DepartmentID OR f.DepartmentID = d.DepartmentID)
    ''')
    return db.fetchall()

def get_user_role(db, user_id):
    db.execute('SELECT Role FROM users WHERE ID = %s', (user_id,))
    return db.fetchone()

def delete_student_by_id(db, user_id):
    db.execute('DELETE FROM student WHERE ID = %s', (user_id,))

def delete_faculty_by_id(db, user_id):
    db.execute('DELETE FROM faculty WHERE ID = %s', (user_id,))

def delete_user_by_id(db, user_id):
    db.execute('DELETE FROM users WHERE ID = %s', (user_id,))

def get_all_courses_with_details(db):
    db.execute('''
        SELECT c.*, d.DepartmentName, u.FirstName, u.LastName
        FROM courses c
        JOIN department d ON c.DepartmentID = d.DepartmentID
        JOIN faculty f ON c.FacultyID = f.FacultyID
        JOIN users u ON f.ID = u.ID
    ''')
    return db.fetchall()

def get_all_faculties_with_details(db):
    db.execute('''
        SELECT f.FacultyID, u.FirstName, u.LastName
        FROM faculty f
        JOIN users u ON f.ID = u.ID
    ''')
    return db.fetchall()

def add_course(db, course_data):
    db.execute('''
        INSERT INTO courses (CourseID, CourseName, CourseCredit, CourseCategory, Semester, DepartmentID, FacultyID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        course_data['course_id'], course_data['course_name'], course_data['credits'],
        course_data['category'], course_data['semester'], course_data['department_id'], course_data['faculty_id']
    ))

def get_department_stats(db):
    db.execute('''
        SELECT d.DepartmentName, COUNT(DISTINCT s.ID) as num_students, COUNT(DISTINCT f.ID) as num_faculty
        FROM department d
        LEFT JOIN student s ON d.DepartmentID = s.DepartmentID
        LEFT JOIN faculty f ON d.DepartmentID = f.DepartmentID
        GROUP BY d.DepartmentName
    ''')
    return db.fetchall()

def get_summary_stats(db):
    db.execute('SELECT COUNT(*) as count FROM student')
    total_students = db.fetchone()['count']
    db.execute('SELECT COUNT(*) as count FROM faculty')
    total_faculty = db.fetchone()['count']
    db.execute('SELECT COUNT(*) as count FROM courses')
    total_courses = db.fetchone()['count']
    return {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses
    }

def add_department(db, dept_data):
    db.execute('INSERT INTO department (DepartmentID, DepartmentName) VALUES (%s, %s)', (dept_data['dept_id'], dept_data['dept_name']))

def get_student_courses(db, student_id):
    db.execute('''
        SELECT c.*, u.FirstName, u.LastName
        FROM courses c
        JOIN enrollment e ON c.CourseID = e.CourseID
        JOIN faculty f ON c.FacultyID = f.FacultyID
        JOIN users u ON f.ID = u.ID
        WHERE e.StudentID = %s
    ''', (student_id,))
    return db.fetchall()

def get_student_assignments(db, student_id):
    db.execute('''
        SELECT cc.*, c.CourseName, s.SubmissionDate, s.Grade
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        JOIN enrollment e ON c.CourseID = e.CourseID
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID AND s.StudentID = e.StudentID
        WHERE e.StudentID = %s AND cc.IsAssignment = 1
        ORDER BY cc.DueDate DESC
    ''', (student_id,))
    return db.fetchall()

def get_student_attendance(db, student_id):
    db.execute('''
        SELECT 
            c.CourseID,
            c.CourseName,
            COUNT(CASE WHEN a.Attendance = 1 THEN 1 END) as attended_classes,
            COUNT(a.Attendance) as total_classes,
            COALESCE(AVG(CAST(a.Attendance as FLOAT)) * 100, 0) as attendance_percentage
        FROM enrollment e
        JOIN courses c ON e.CourseID = c.CourseID
        LEFT JOIN attendance a ON e.CourseID = a.CourseID AND e.StudentID = a.StudentID
        WHERE e.StudentID = %s
        GROUP BY c.CourseID, c.CourseName
    ''', (student_id,))
    return db.fetchall()

def get_student_grades(db, student_id):
    db.execute('''
        SELECT 
            c.CourseID,
            c.CourseName,
            c.CourseCredit,
            COALESCE(AVG(s.Grade), 0) as average_grade,
            COUNT(DISTINCT cc.CourseContentID) as total_assignments,
            COUNT(DISTINCT s.SubmissionID) as completed_assignments
        FROM enrollment e
        JOIN courses c ON e.CourseID = c.CourseID
        LEFT JOIN coursecontent cc ON c.CourseID = cc.CourseID AND cc.IsAssignment = 1
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID AND s.StudentID = e.StudentID
        WHERE e.StudentID = %s
        GROUP BY c.CourseID, c.CourseName, c.CourseCredit
    ''', (student_id,))
    return db.fetchall()

def get_student_profile(db, student_id):
    db.execute('''
        SELECT s.*, u.*, d.DepartmentName
        FROM student s
        INNER JOIN users u ON s.ID = u.ID
        INNER JOIN department d ON s.DepartmentID = d.DepartmentID
        WHERE s.ID = %s
    ''', (student_id,))
    return db.fetchone()

def add_assignment(db, assignment_data):
    db.execute('''
        INSERT INTO CourseContent 
        (CourseID, CCName, Description, UploadDate, DueDate, TotalMarks) 
        VALUES (%s, %s, %s, NOW(), %s, %s)
    ''', (assignment_data['course_id'], assignment_data['name'], assignment_data['description'], 
          assignment_data['due_date'], assignment_data['total_marks']))

def get_faculty_courses(db, faculty_id):
    db.execute('''
        SELECT c.*, d.DepartmentName,
               (SELECT COUNT(*) FROM Enrollment WHERE CourseID = c.CourseID) as student_count,
               (SELECT COUNT(*) FROM CourseContent WHERE CourseID = c.CourseID AND IsAssignment = 1) as assignment_count
        FROM courses c
        JOIN department d ON c.DepartmentID = d.DepartmentID
        WHERE c.FacultyID = %s
    ''', (faculty_id,))
    return db.fetchall()

def get_faculty_assignments(db, faculty_id):
    db.execute('''
        SELECT 
            cc.*,
            c.CourseName,
            COUNT(DISTINCT s.SubmissionID) as submission_count,
            (SELECT COUNT(DISTINCT e.StudentID) 
             FROM enrollment e 
             WHERE e.CourseID = c.CourseID) as total_students
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID
        WHERE c.FacultyID = %s AND cc.IsAssignment = 1
        GROUP BY cc.CourseContentID, c.CourseName
        ORDER BY cc.UploadDate DESC
    ''', (faculty_id,))
    return db.fetchall()

def get_faculty_reports(db, faculty_id):
    db.execute('''
        SELECT c.CourseID, c.CourseName,
               COUNT(DISTINCT e.StudentID) as enrolled_students,
               COUNT(DISTINCT cc.CourseContentID) as total_assignments,
               AVG(s.Grade) as average_grade,
               (SELECT AVG(Attendance) * 100 
                FROM attendance 
                WHERE CourseID = c.CourseID) as average_attendance
        FROM courses c
        LEFT JOIN enrollment e ON c.CourseID = e.CourseID
        LEFT JOIN coursecontent cc ON c.CourseID = cc.CourseID AND cc.IsAssignment = 1
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID
        WHERE c.FacultyID = %s
        GROUP BY c.CourseID
    ''', (faculty_id,))
    course_stats = db.fetchall()
    
    db.execute('''
        SELECT cc.CourseContentID, cc.CCName, c.CourseName,
               COUNT(DISTINCT s.StudentID) as submissions,
               (SELECT COUNT(*) FROM enrollment WHERE CourseID = c.CourseID) as total_students,
               AVG(s.Grade) as average_grade
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID
        WHERE c.FacultyID = %s AND cc.IsAssignment = 1
        GROUP BY cc.CourseContentID
        ORDER BY cc.UploadDate DESC
    ''', (faculty_id,))
    assignment_stats = db.fetchall()
    
    return {
        'course_stats': course_stats,
        'assignment_stats': assignment_stats
    }

def get_faculty_students_data(db, faculty_id):
    db.execute('''
        SELECT CourseID, CourseName 
        FROM courses 
        WHERE FacultyID = %s
    ''', (faculty_id,))
    faculty_courses = db.fetchall()

    db.execute('''
        SELECT DISTINCT s.ID, s.RegistrationNo, u.FirstName, u.LastName
        FROM student s
        JOIN users u ON s.ID = u.ID
        WHERE s.ID NOT IN (
            SELECT e.StudentID
            FROM enrollment e
            JOIN courses c ON e.CourseID = c.CourseID
            WHERE c.FacultyID = %s
        )
    ''', (faculty_id,))
    available_students = db.fetchall()

    db.execute('''
        SELECT s.ID, s.RegistrationNo, u.FirstName, u.LastName,
            c.CourseID, c.CourseName, d.DepartmentName,
            COALESCE(AVG(CAST(a.Attendance as FLOAT)), 0) * 100 as attendance_percentage
        FROM enrollment e
        JOIN student s ON e.StudentID = s.ID
        JOIN users u ON s.ID = u.ID
        JOIN courses c ON e.CourseID = c.CourseID
        JOIN department d ON s.DepartmentID = d.DepartmentID
        LEFT JOIN attendance a ON e.StudentID = a.StudentID AND e.CourseID = a.CourseID
        WHERE c.FacultyID = %s
        GROUP BY s.ID, s.RegistrationNo, u.FirstName, u.LastName, 
                 c.CourseID, c.CourseName, d.DepartmentName
    ''', (faculty_id,))
    enrolled_students = db.fetchall()

    return {
        'faculty_courses': faculty_courses,
        'available_students': available_students,
        'enrolled_students': enrolled_students
    }

def enroll_student(db, student_id, course_id):
    db.execute('''
        INSERT INTO enrollment (StudentID, CourseID, EnrollmentDate)
        VALUES (%s, %s, CURRENT_DATE())
    ''', (student_id, course_id))

def unenroll_student(db, student_id, course_id):
    db.execute('''
        DELETE FROM enrollment
        WHERE StudentID = %s AND CourseID = %s
    ''', (student_id, course_id))

def get_faculty_profile(db, faculty_id):
    db.execute('''
        SELECT s.*, u.*, d.DepartmentName
        FROM faculty s
        INNER JOIN users u ON s.ID = u.ID
        INNER JOIN department d ON s.DepartmentID = d.DepartmentID
        WHERE s.ID = %s
    ''', (faculty_id,))
    return db.fetchone()

def get_faculty_course_details(db, course_id, faculty_id):
    db.execute('''
        SELECT c.*, d.DepartmentName,
               COUNT(DISTINCT e.StudentID) as student_count,
               COUNT(DISTINCT cc.CourseContentID) as assignment_count,
               AVG(a.Attendance) * 100 as average_attendance
        FROM courses c
        LEFT JOIN department d ON c.DepartmentID = d.DepartmentID
        LEFT JOIN enrollment e ON c.CourseID = e.CourseID
        LEFT JOIN coursecontent cc ON c.CourseID = cc.CourseID AND cc.IsAssignment = 1
        LEFT JOIN attendance a ON c.CourseID = a.CourseID
        WHERE c.CourseID = %s AND c.FacultyID = %s
        GROUP BY c.CourseID
    ''', (course_id, faculty_id))
    course = db.fetchone()
    
    db.execute('''
        SELECT cc.*, 
               COUNT(DISTINCT s.SubmissionID) as submission_count
        FROM coursecontent cc
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID
        WHERE cc.CourseID = %s AND cc.IsAssignment = 1
        GROUP BY cc.CourseContentID
        ORDER BY cc.UploadDate DESC
    ''', (course_id,))
    assignments = db.fetchall()
    
    return {
        'course': course,
        'assignments': assignments
    }

def get_user_for_edit(db, user_id):
    db.execute('''
        SELECT u.*, 
               COALESCE(s.RegistrationNo, f.FacultyID) as identifier,
               d.DepartmentName
        FROM users u
        LEFT JOIN student s ON u.ID = s.ID
        LEFT JOIN faculty f ON u.ID = f.ID
        LEFT JOIN department d ON s.DepartmentID = d.DepartmentID 
            OR f.DepartmentID = d.DepartmentID
        WHERE u.ID = %s
    ''', (user_id,))
    return db.fetchone()

def update_user(db, user_id, user_data):
    db.execute('''
        UPDATE users 
        SET Username = %s, FirstName = %s, LastName = %s, 
            Email = %s, Role = %s
        WHERE ID = %s
    ''', (
        user_data['username'],
        user_data['firstName'],
        user_data['lastName'],
        user_data['email'],
        user_data['role'],
        user_id
    ))

def get_attendance_view_data(db, course_id):
    db.execute('''
        SELECT c.*, u.FirstName as FacultyFirstName, u.LastName as FacultyLastName
        FROM courses c
        JOIN faculty f ON c.FacultyID = f.ID
        JOIN users u ON f.ID = u.ID
        WHERE c.CourseID = %s
    ''', (course_id,))
    course = db.fetchone()

    if not course:
        return None, None, None, None, None, None

    db.execute('''
        SELECT 
            s.RegistrationNo,
            u.FirstName,
            u.LastName,
            COUNT(CASE WHEN a.Attendance = 1 THEN 1 END) as classes_attended,
            COUNT(a.Attendance) as total_classes,
            COALESCE(AVG(a.Attendance) * 100, 0) as attendance_percentage
        FROM student s
        JOIN users u ON s.ID = u.ID
        JOIN enrollment e ON s.ID = e.StudentID
        LEFT JOIN attendance a ON s.ID = a.StudentID AND a.CourseID = %s
        WHERE e.CourseID = %s
        GROUP BY s.ID, s.RegistrationNo, u.FirstName, u.LastName
        ORDER BY u.FirstName, u.LastName
    ''', (course_id, course_id))
    attendance_records = db.fetchall()

    total_students = len(attendance_records)
    db.execute('SELECT COUNT(DISTINCT Date) as total FROM attendance WHERE CourseID = %s', (course_id,))
    total_classes_res = db.fetchone()
    total_classes = total_classes_res['total'] if total_classes_res else 0

    if attendance_records:
        average_attendance = sum(record['attendance_percentage'] for record in attendance_records) / len(attendance_records)
    else:
        average_attendance = 0

    db.execute('SELECT DISTINCT DATE(Date) as date FROM attendance WHERE CourseID = %s ORDER BY Date DESC', (course_id,))
    dates = [row['date'].strftime('%Y-%m-%d') for row in db.fetchall()]

    return course, attendance_records, total_students, total_classes, average_attendance, dates

def get_course_for_attendance(db, course_id):
    db.execute('''
        SELECT c.*, u.FirstName as FacultyFirstName, u.LastName as FacultyLastName
        FROM courses c
        JOIN faculty f ON c.FacultyID = f.FacultyID
        JOIN users u ON f.ID = u.ID
        WHERE c.CourseID = %s
    ''', (course_id,))
    return db.fetchone()

def get_students_for_attendance(db, course_id):
    db.execute('''
        SELECT s.ID, s.RegistrationNo, u.FirstName, u.LastName
        FROM student s
        JOIN users u ON s.ID = u.ID
        JOIN courses c ON s.DepartmentID = c.DepartmentID
        WHERE c.CourseID = %s
        ORDER BY s.RegistrationNo
    ''', (course_id,))
    return db.fetchall()

def save_attendance(db, course_id, attendance_data):
    for student_id, is_present in attendance_data.items():
        db.execute('''
            INSERT INTO attendance 
            (StudentID, CourseID, Date, Attendance)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            Date = %s,
            Attendance = %s
        ''', (student_id, course_id, attendance_data['datetime_str'], is_present, 
              attendance_data['datetime_str'], is_present))

def get_assignment_for_submission(db, assignment_id, student_id):
    db.execute('''
        SELECT 
            cc.*,
            c.CourseName,
            DATE_FORMAT(cc.DueDate, '%%Y-%%m-%%d %%H:%%i') as formatted_due_date,
            s.SubmissionID,
            s.SubmissionDate
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        LEFT JOIN submissions s ON cc.CourseContentID = s.CCID 
            AND s.StudentID = %s
        WHERE cc.CourseContentID = %s
    ''', (student_id, assignment_id))
    return db.fetchone()

def check_existing_submission(db, assignment_id, student_id):
    db.execute('''
        SELECT SubmissionID FROM submissions 
        WHERE CCID = %s AND StudentID = %s
    ''', (assignment_id, student_id))
    return db.fetchone()

def create_submission(db, student_id, assignment_id, file_path):
    db.execute('''
        INSERT INTO submissions (StudentID, CCID, FileUrl, SubmissionDate)
        VALUES (%s, %s, %s, NOW())
    ''', (student_id, assignment_id, file_path))

def get_assignment_submissions(db, assignment_id, faculty_id):
    db.execute('''
        SELECT cc.*, c.CourseName
        FROM coursecontent cc
        JOIN courses c ON cc.CourseID = c.CourseID
        WHERE cc.CourseContentID = %s AND c.FacultyID = %s
    ''', (assignment_id, faculty_id))
    assignment = db.fetchone()
    if not assignment:
        return None, None, None

    db.execute('''
        SELECT 
            s.ID as StudentID,
            u.FirstName,
            u.LastName,
            sub.SubmissionDate,
            sub.FileUrl,
            sub.Grade,
            (SELECT COUNT(*) 
             FROM submissions 
             WHERE CCID = %s) as submission_count
        FROM student s
        JOIN users u ON s.ID = u.ID
        JOIN enrollment e ON s.ID = e.StudentID
        LEFT JOIN submissions sub ON s.ID = sub.StudentID AND sub.CCID = %s
        WHERE e.CourseID = %s
        ORDER BY u.FirstName, u.LastName
    ''', (assignment_id, assignment_id, assignment['CourseID']))
    submissions = db.fetchall()

    db.execute('''
        SELECT COUNT(DISTINCT e.StudentID) as total
        FROM enrollment e
        WHERE e.CourseID = %s
    ''', (assignment['CourseID'],))
    total_students = db.fetchone()['total']

    return assignment, submissions, total_students