-- USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    reg_no VARCHAR(50)  UNIQUE,
	pf VARCHAR(50)  UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- =========================================
-- USER DEVICE INFO TABLE 
-- =========================================

CREATE TABLE public.user_deviceinfo (
    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    visitor_id TEXT NOT NULL,

    user_agent TEXT,
    platform VARCHAR(100),
    language VARCHAR(50),
    screen_resolution VARCHAR(20),
    timezone VARCHAR(100),
    device_memory VARCHAR(20),
    hardware_concurrency VARCHAR(20),

    status VARCHAR(20) DEFAULT NULL,
    -- NULL = active/normal
    -- 'restored' = allowed new device login flow

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- relationships
    CONSTRAINT fk_user_device
        FOREIGN KEY (user_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE,

    -- prevent duplicate device registration
    CONSTRAINT unique_user_device UNIQUE (user_id, visitor_id)
);

CREATE TABLE public.push_subscriptions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_push_student
        FOREIGN KEY (student_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE
);
-- =========================================
-- UNITS TABLE 
-- =========================================

CREATE TABLE public.units (
    id SERIAL PRIMARY KEY,

    unit_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL
);
-- =========================================
-- UNIT ASSIGNMENTS TABLE 
-- =========================================

CREATE TABLE public.unit_assignments (
    assignment_id SERIAL PRIMARY KEY,

    lecturer_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- relationships
    CONSTRAINT fk_assignment_lecturer
        FOREIGN KEY (lecturer_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_unit
        FOREIGN KEY (unit_id)
        REFERENCES public.units (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_course
        FOREIGN KEY (course_id)
        REFERENCES public.course (course_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_session
        FOREIGN KEY (session_id)
        REFERENCES public.academic_sessions (session_id)
        ON DELETE CASCADE,

    -- prevent duplicate assignment
    CONSTRAINT unique_unit_course_session
        UNIQUE (unit_id, course_id, session_id)
);
-- =========================================
-- ENROLLMENTS TABLE 
-- =========================================

CREATE TABLE public.enrollments (
    enrollment_id SERIAL PRIMARY KEY,

    student_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- relationships
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollment_unit
        FOREIGN KEY (unit_id)
        REFERENCES public.units (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollment_session
        FOREIGN KEY (session_id)
        REFERENCES public.academic_sessions (session_id)
        ON DELETE CASCADE,

    -- prevent duplicate enrollment
    CONSTRAINT unique_student_unit_session
        UNIQUE (student_id, unit_id, session_id)
);
-- =========================================
-- COURSE_UNITS TABLE 
-- =========================================

CREATE TABLE public.course_units (
    course_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,

    -- composite primary key (prevents duplicates)
    PRIMARY KEY (course_id, unit_id),

    -- relationships
    CONSTRAINT fk_course_units_course
        FOREIGN KEY (course_id)
        REFERENCES public.course (course_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_course_units_unit
        FOREIGN KEY (unit_id)
        REFERENCES public.units (id)
        ON DELETE CASCADE
);
-- =========================================
-- COURSE_UNITS TABLE
-- =========================================

CREATE TABLE public.course_units (
    course_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,

    -- composite primary key ensures no duplicates
    PRIMARY KEY (course_id, unit_id),

    -- course relationship
    CONSTRAINT fk_course_units_course
        FOREIGN KEY (course_id)
        REFERENCES public.course (course_id)
        ON DELETE CASCADE,

    -- unit relationship
    CONSTRAINT fk_course_units_unit
        FOREIGN KEY (unit_id)
        REFERENCES public.units (id)
        ON DELETE CASCADE
);
-- =========================================
-- COURSE TABLE
-- =========================================

CREATE TABLE public.course (
    course_id SERIAL PRIMARY KEY,

    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL
);
-- =========================================
-- CLASS SESSION TABLE
-- =========================================

CREATE TABLE public.class_session (
    id SERIAL PRIMARY KEY,

    unit_assignment_id INTEGER NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',

    started_at TIMESTAMP,
    ended_at TIMESTAMP,

    lecturer_lat DOUBLE PRECISION,
    lecturer_lng DOUBLE PRECISION,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- relationship
    CONSTRAINT fk_class_session_assignment
        FOREIGN KEY (unit_assignment_id)
        REFERENCES public.unit_assignments (assignment_id)
        ON DELETE CASCADE
);

-- =========================================
-- ATTENDANCE TABLE
-- =========================================

CREATE TABLE public.attendance (
    id SERIAL PRIMARY KEY,

    student_id INTEGER NOT NULL,
    class_session_id INTEGER NOT NULL,

    status VARCHAR(20) DEFAULT 'absent',
    method VARCHAR(20) DEFAULT 'system',

    attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- relationships
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_attendance_session
        FOREIGN KEY (class_session_id)
        REFERENCES public.class_session (id)
        ON DELETE CASCADE,

    -- prevent duplicate marking
    CONSTRAINT unique_student_session
        UNIQUE (student_id, class_session_id),

    -- valid status values
    CONSTRAINT chk_attendance_status
        CHECK (status IN ('absent', 'present')),

    -- valid marking methods
    CONSTRAINT chk_attendance_method
        CHECK (method IN ('system', 'gps', 'bluetooth', 'manual'))
);
-- =========================================
-- ACADEMIC SESSIONS TABLE
-- =========================================

CREATE TABLE public.academic_sessions (
    session_id SERIAL PRIMARY KEY,

    academic_year_start INTEGER NOT NULL,
    academic_year_end INTEGER NOT NULL,

    semester INTEGER NOT NULL,

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    is_active BOOLEAN DEFAULT FALSE,

    -- only semester 1 or 2 allowed
    CONSTRAINT chk_semester
        CHECK (semester IN (1, 2))
);

-- =========================================
-- STEP 1: CHECK REQUIRED DATA EXISTS
-- =========================================
-- Ensure the lecturer, unit, course, and academic session exist first.

-- Example checks (optional but recommended):
-- SELECT * FROM users WHERE id = 1;
-- SELECT * FROM units WHERE id = 2;
-- SELECT * FROM course WHERE course_id = 1;
-- SELECT * FROM academic_sessions WHERE is_active = true;


-- =========================================
-- STEP 2: GET ACTIVE ACADEMIC SESSION
-- =========================================
-- This ensures lecturer is assigned under the current semester/year.

-- We use subquery so no need to manually copy session_id
-- It automatically picks the active academic session.

-- =========================================
-- STEP 3: ASSIGN LECTURER TO UNIT
-- =========================================

select * from unit_assignments;
select * from course;
select * from units;
SELECT * FROM users WHERE role = 'lecturer';

INSERT INTO unit_assignments (
    lecturer_id,
    unit_id,
    course_id,
    session_id
)
VALUES (
    14,  -- lecturer_id (change this)
    5,  -- unit_id (change this)
    2,  -- course_id (change this)

    -- Automatically fetch ACTIVE academic session
    (
        SELECT session_id
        FROM public.academic_sessions
        WHERE is_active = true
        LIMIT 1
    )
);

-- =========================================
-- STEP 1: CHECK DATA EXISTS
-- =========================================
-- Make sure course and unit exist

-- SELECT * FROM course WHERE course_id = 1;
-- SELECT * FROM units WHERE id = 2;


-- =========================================
-- STEP 2: ASSIGN UNIT TO COURSE
-- =========================================

INSERT INTO public.course_units (
    course_id,
    unit_id
)
VALUES (
    1,  -- course_id (e.g. Computer Science)
    2   -- unit_id (e.g. Databases)
);


-- =========================================
-- STEP 3: PREVENT DUPLICATES (OPTIONAL BUT SAFE)
-- =========================================
-- This ensures the same unit is not assigned twice to same course

-- If already exists → do nothing

ON CONFLICT (course_id, unit_id)
DO NOTHING;
