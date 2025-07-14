from fastapi import APIRouter, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import time, os, shutil
from mysql.connector import Error
from werkzeug.security import check_password_hash

# Import helper functions
from database import get_db
from auth import get_current_user
from . import database_queries as db_queries

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/home")
    from core.config import templates
    return templates.TemplateResponse("login.html", {"request": request, "msg": ""})

@router.post("/login")
async def login(
    request: Request,
    db=Depends(get_db)
):
    from core.config import templates
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    account = db_queries.get_user_by_email(db, email)
    if account and check_password_hash(account['PasswordHash'], password):
        request.session['loggedin'] = True
        request.session['id'] = account['ID']
        request.session['username'] = account['UserName']
        request.session['role'] = account['Role']
        return RedirectResponse(url="/home", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "msg": "Incorrect username/password!"
    })

@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    db=Depends(get_db)
):
    from core.config import templates
    departments = db_queries.get_all_departments(db)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "departments": departments
    })

@router.post("/register")
async def register(
    request: Request,
    db=Depends(get_db)
):
    from core.config import templates
    form = await request.form()
    try:
        user_data = {
            'ID': int(form['ID']),
            'username': form['username'],
            'password': form['password'],
            'firstname': form['firstname'],
            'lastname': form['lastname'],
            'email': form['email'],
            'role': form['role']
        }
        db_queries.create_user(db, user_data)
        
        if user_data['role'] == 'student':
            student_data = {
                'ID': user_data['ID'],
                'registration_no': form['registration_no'],
                'phone': form['phone'],
                'class': form['class'],
                'dob': form['dob'],
                'semester': form['semester'],
                'department_id': form['department_id']
            }
            db_queries.create_student(db, student_data)
        elif user_data['role'] == 'faculty':
            faculty_data = {
                'ID': user_data['ID'],
                'faculty_id': form['faculty_id'],
                'phone': form['phone'],
                'qualification': form['qualification'],
                'level': form['level'],
                'department_id': form['department_id']
            }
            db_queries.create_faculty(db, faculty_data)
        
        return RedirectResponse(url="/login", status_code=303)
    
    except Error as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"Database error: {str(e)}"
        })

@router.get("/home", response_class=HTMLResponse)
async def home(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates
    if not current_user:
        return RedirectResponse(url="/login")
    
    if current_user['role'] == 'admin':
        departments = db_queries.get_all_departments(db)
        stats = db_queries.get_admin_dashboard_stats(db)
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "username": current_user['username'],
            "departments": departments,
            **stats
        })
    
    elif current_user['role'] == 'faculty':
        data = db_queries.get_faculty_dashboard_data(db, current_user['id'])
        return templates.TemplateResponse("faculty_dashboard.html", {
            "request": request,
            "username": current_user['username'],
            **data
        })
    
    else:
        data = db_queries.get_student_dashboard_data(db, current_user['id'])
        total_courses = len(data['enrolled_courses'])
        avg_attendance = round(sum(course['attendance_percentage'] for course in data['enrolled_courses']) / total_courses if total_courses > 0 else 0,2)
        total_assignments = sum(course['total_assignments'] for course in data['enrolled_courses'])
        completed_assignments = sum(course['completed_assignments'] for course in data['enrolled_courses'])

        return templates.TemplateResponse("student_dashboard.html", {
            "request": request,
            "username": current_user['username'],
            "student": data['student'],
            "courses": data['enrolled_courses'],
            "assignments": data['recent_assignments'],
            "stats": {
                "total_courses": total_courses,
                "avg_attendance": avg_attendance,
                "total_assignments": total_assignments,
                "completed_assignments": completed_assignments,
            }
        })

@router.get("/course/{course_id}", response_class=HTMLResponse)
@router.post("/course/{course_id}", response_class=HTMLResponse)
async def course(
    course_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user:
        return RedirectResponse(url="/login")
    
    course = db_queries.get_course_details(db, course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    contents = db_queries.get_course_content(db, course_id)
    
    is_faculty = (current_user['role'] == 'faculty' and 
                 current_user['id'] == course['FacultyID'])
    
    if request.method == "POST" and is_faculty:
        form = await request.form()
        if 'add_content' in form:
            content_data = {
                'content_name': form['content_name'],
                'description': form['description'],
                'file_url': form['file_url'],
                'is_assignment': 'is_assignment' in form,
                'course_id': course_id,
                'user_id': current_user['id']
            }
            db_queries.add_course_content(db, content_data)
            return RedirectResponse(url=f"/course/{course_id}", status_code=303)
    
    return templates.TemplateResponse("course.html", {
        "request": request,
        "course": course,
        "contents": contents,
        "is_faculty": is_faculty
    })



@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    users = db_queries.get_all_users_with_details(db)
    
    return templates.TemplateResponse("admin/manage_users.html", {
        "request": request,
        "users": users,
        "current_user": current_user,
        "active_page": "manage_users"
    })

@router.delete("/admin/users/delete/{user_id}")
async def delete_user(
    user_id: int,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        user_role = db_queries.get_user_role(db, user_id)
        
        if user_role['Role'].lower() == 'student':
            db_queries.delete_student_by_id(db, user_id)
        elif user_role['Role'].lower() == 'faculty':
            db_queries.delete_faculty_by_id(db, user_id)
            
        db_queries.delete_user_by_id(db, user_id)
        
        return {"success": True}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/courses", response_class=HTMLResponse)
async def admin_courses(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    courses = db_queries.get_all_courses_with_details(db)
    departments = db_queries.get_all_departments(db)
    faculties = db_queries.get_all_faculties_with_details(db)
    
    return templates.TemplateResponse("admin/manage_courses.html", {
        "request": request,
        "courses": courses,
        "departments": departments,
        "faculties": faculties,
        "current_user": current_user,
        "active_page": "manage_courses"
    })

@router.post("/admin/courses/add")
async def add_course(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    form = await request.form()
    try:
        course_data = {
            'course_id': form['course_id'],
            'course_name': form['course_name'],
            'credits': form['credits'],
            'category': form['category'],
            'semester': form['semester'],
            'department_id': form['department_id'],
            'faculty_id': form['faculty_id']
        }
        db_queries.add_course(db, course_data)
        return RedirectResponse(url="/admin/courses", status_code=303)
    except Error as e:
        return {"error": str(e)}

@router.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    dept_stats = db_queries.get_department_stats(db)
    summary_stats = db_queries.get_summary_stats(db)
    
    return templates.TemplateResponse("admin/reports.html", {
        "request": request,
        "dept_stats": dept_stats,
        "current_user": current_user,
        **summary_stats
    })

@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    departments = db_queries.get_all_departments(db)
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "departments": departments,
        "current_user": current_user
    })

@router.post("/admin/department/add")
async def add_department(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    form = await request.form()
    try:
        dept_data = {
            'dept_id': form['dept_id'],
            'dept_name': form['dept_name']
        }
        db_queries.add_department(db, dept_data)
        return RedirectResponse(url="/admin/settings", status_code=303)
    except Error as e:
        return {"error": str(e)}

@router.get("/student/courses", response_class=HTMLResponse)
async def student_courses(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    courses = db_queries.get_student_courses(db, current_user['id'])
    
    return templates.TemplateResponse("student/courses.html", {
        "request": request,
        "courses": courses,
        "username": current_user['username']
    })

@router.get("/student/assignments", response_class=HTMLResponse)
async def student_assignments(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    assignments = db_queries.get_student_assignments(db, current_user['id'])
    
    return templates.TemplateResponse("student/assignments.html", {
        "request": request,
        "assignments": assignments,
        "username": current_user['username']
    })

@router.get("/student/attendance", response_class=HTMLResponse)
async def student_attendance(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    attendance = db_queries.get_student_attendance(db, current_user['id'])
    
    return templates.TemplateResponse("student/attendance.html", {
        "request": request,
        "attendance": attendance,
        "username": current_user['username']
    })

@router.get("/student/grades", response_class=HTMLResponse)
async def student_grades(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    grades = db_queries.get_student_grades(db, current_user['id'])
    
    return templates.TemplateResponse("student/grades.html", {
        "request": request,
        "grades": grades,
        "username": current_user['username']
    })

@router.get("/student/profile", response_class=HTMLResponse)
async def student_profile(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    profile = db_queries.get_student_profile(db, current_user['id'])
    
    return templates.TemplateResponse("student/profile.html", {
        "request": request,
        "profile": profile,
        "username": current_user['username']
    })

@router.post("/faculty/assignment/add")
async def add_assignment(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    form = await request.form()
    assignment_data = {
        'course_id': form['course_id'],
        'name': form['name'],
        'description': form['description'],
        'due_date': form['due_date'],
        'total_marks': form['total_marks']
    }
    
    db_queries.add_assignment(db, assignment_data)
    
    return RedirectResponse(url=f"/faculty/course/{assignment_data['course_id']}", status_code=303)

@router.get("/faculty/courses")
async def faculty_courses(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    courses = db_queries.get_faculty_courses(db, current_user['id'])
    
    return templates.TemplateResponse("/faculty/faculty_courses.html", {
        "request": request,
        "courses": courses,
        "username": current_user['username']
    })

@router.get("/faculty/assignments")
async def faculty_assignments(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    assignments = db_queries.get_faculty_assignments(db, current_user['id'])
    
    return templates.TemplateResponse("faculty/faculty_assignments.html", {
        "request": request,
        "assignments": assignments,
        "username": current_user['username']
    })


@router.get("/faculty/reports")
async def faculty_reports(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    report_data = db_queries.get_faculty_reports(db, current_user['id'])
    
    return templates.TemplateResponse("faculty/reports.html", {
        "request": request,
        "course_stats": report_data['course_stats'],
        "assignment_stats": report_data['assignment_stats'],
        "username": current_user['username']
    })

@router.get("/faculty/students")
async def faculty_students(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")

    student_data = db_queries.get_faculty_students_data(db, current_user['id'])

    return templates.TemplateResponse("faculty/students.html", {
        "request": request,
        "faculty_courses": student_data['faculty_courses'],
        "available_students": student_data['available_students'],
        "enrolled_students": student_data['enrolled_students'],
        "current_user": current_user
    })

@router.post("/faculty/enroll-student")
async def enroll_student(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")

    form = await request.form()
    student_id = form.get('student_id')
    course_id = form.get('course_id')

    try:
        # Assuming you might want to check if the faculty is authorized for the course
        # This check is not strictly necessary if you trust the frontend
        course = db_queries.get_course_details(db, course_id)
        if not course or course['FacultyID'] != current_user['id']:
             raise HTTPException(status_code=403, detail="Unauthorized")

        db_queries.enroll_student(db, student_id, course_id)
        
        return RedirectResponse(url="/faculty/students", status_code=303)
    except Error as e:
        return {"error": str(e)}

@router.post("/faculty/unenroll-student")
async def unenroll_student(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")

    form = await request.form()
    student_id = form.get('student_id')
    course_id = form.get('course_id')

    try:
        # Assuming you might want to check if the faculty is authorized for the course
        course = db_queries.get_course_details(db, course_id)
        if not course or course['FacultyID'] != current_user['id']:
             raise HTTPException(status_code=403, detail="Unauthorized")

        db_queries.unenroll_student(db, student_id, course_id)
        
        return RedirectResponse(url="/faculty/students", status_code=303)
    except Error as e:
        return {"error": str(e)}







@router.get("/faculty/profile", response_class=HTMLResponse)
async def faculty_profile(
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    profile = db_queries.get_faculty_profile(db, current_user['id'])
    
    return templates.TemplateResponse("faculty/profile.html", {
        "request": request,
        "profile": profile,
        "username": current_user['username']
    })

@router.get("/faculty/course/{course_id}")
async def faculty_course(
    course_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    details = db_queries.get_faculty_course_details(db, course_id, current_user['id'])
    
    if not details['course']:
        raise HTTPException(
            status_code=404,
            detail=f"Course with ID {course_id} not found or you don't have access to it."
        )
    
    return templates.TemplateResponse("faculty/faculty_course.html", {
        "request": request,
        "course": details['course'],
        "assignments": details['assignments'],
        "username": current_user['username']
    })

@router.get("/admin/users/edit/{user_id}", response_class=HTMLResponse)
async def edit_user_page(
    user_id: int,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    user = db_queries.get_user_for_edit(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("admin/edit_user.html", {
        "request": request,
        "user": user,
        "current_user": current_user
    })

@router.post("/admin/users/edit/{user_id}", response_class=HTMLResponse)
async def update_user(
    user_id: int,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'admin':
        return RedirectResponse(url="/login")
    
    form = await request.form()
    user_data = {
        'username': form.get('username'),
        'firstName': form.get('firstName'),
        'lastName': form.get('lastName'),
        'email': form.get('email'),
        'role': form.get('role')
    }
    try:
        db_queries.update_user(db, user_id, user_data)
        
        request.session['message'] = 'User updated successfully'
        return RedirectResponse(url="/admin/users", status_code=303)
    
    except Error as e:
        return templates.TemplateResponse("admin/edit_user.html", {
            "request": request,
            "user": dict(form),
            "current_user": current_user,
            "error": str(e)
        })

@router.get("/course/{course_id}/mark-attendance")
async def mark_attendance_page(
    course_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from core.config import templates 
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    course = db_queries.get_course_for_attendance(db, course_id)
    
    students = db_queries.get_students_for_attendance(db, course_id)
    
    return templates.TemplateResponse("faculty/mark_attendance.html", {
        "request": request,
        "course": course,
        "students": students
    })

@router.post("/course/{course_id}/save-attendance")
async def save_attendance(
    course_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    form = await request.form()
    attendance_date = form.get('attendance_date')
    class_time = form.get('class_time')
    
    datetime_str = f"{attendance_date} {class_time}"
    attendance_data = {
        'datetime_str': datetime_str
    }
    for key, value in form.items():
        if key.startswith('attendance_') and key != 'attendance_date':
            student_id = int(key.split('_')[1])
            is_present = value == 'present'
            attendance_data[student_id] = is_present

    try:
        db_queries.save_attendance(db, course_id, attendance_data)
        
        return RedirectResponse(url=f"/course/{course_id}#attendance", status_code=303)
    except Error as e:
        return {"error": str(e)}

@router.get("/assignment/submit/{assignment_id}", response_class=HTMLResponse)
async def show_submission_form(
    assignment_id: int,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from fastapp import templates 
    if not current_user or current_user['role'] != 'student':
        return RedirectResponse(url="/login")
    
    assignment = db_queries.get_assignment_for_submission(db, assignment_id, current_user['id'])
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment['SubmissionID']:
        return RedirectResponse(url="/student/assignments")
    
    return templates.TemplateResponse("student/submit_assignment.html", {
        "request": request,
        "assignment": assignment,
        "username": current_user['username']
    })

@router.post("/assignment/submit/{assignment_id}")
async def submit_assignment(
    assignment_id: int,
    request: Request,
    submission_file: UploadFile = File(...),
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user or current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        if db_queries.check_existing_submission(db, assignment_id, current_user['id']):
            raise HTTPException(status_code=400, detail="Assignment already submitted")
        
        if submission_file:
            file_extension = submission_file.filename.split('.')[-1].lower()
            allowed_extensions = {'pdf', 'doc', 'docx', 'zip'}
            
            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=400, detail="Invalid file type")
            
            filename = f"{current_user['id']}_{assignment_id}_{int(time.time())}.{file_extension}"
            file_path = f"static/submissions/{filename}"
            
            os.makedirs("static/submissions", exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(submission_file.file, buffer)
            
            db_queries.create_submission(db, current_user['id'], assignment_id, file_path)
            
            return RedirectResponse(url="/student/assignments", status_code=303)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/faculty/assignment/{assignment_id}/submissions", response_class=HTMLResponse)
async def view_submissions(
    assignment_id: int,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from fastapp import templates
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    assignment, submissions, total_students = db_queries.get_assignment_submissions(db, assignment_id, current_user['id'])
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return templates.TemplateResponse("faculty/view_submissions.html", {
        "request": request,
        "assignment": assignment,
        "submissions": submissions,
        "total_students": total_students,
        "username": current_user['username']
    })

@router.get("/course/{course_id}/view-attendance")
async def view_attendance(
    course_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from fastapp import templates
    if not current_user or current_user['role'] != 'faculty':
        return RedirectResponse(url="/login")
    
    course, attendance_records, total_students, total_classes, average_attendance, dates = db_queries.get_attendance_view_data(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return templates.TemplateResponse("faculty/view_attendance.html", {
        "request": request,
        "course": course,
        "attendance_records": attendance_records,
        "total_students": total_students,
        "total_classes": total_classes,
        "average_attendance": average_attendance,
        "dates": dates
    })