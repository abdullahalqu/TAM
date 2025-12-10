# Database ERD
## Task Management System

---

## Schema Diagram

```
┌─────────────────────────────────────┐
│          USERS                      │
├─────────────────────────────────────┤
│ PK  id              UUID            │
│     email           VARCHAR(255)    │ UNIQUE
│     hashed_password VARCHAR(255)    │
│     full_name       VARCHAR(255)    │ NULLABLE
│     is_active       BOOLEAN         │ DEFAULT TRUE
│     created_at      TIMESTAMP       │
│     updated_at      TIMESTAMP       │
└─────────────────────────────────────┘
              │ 1
              │
              │ has many
              │
              ▼ N
┌─────────────────────────────────────┐
│          TASKS                      │
├─────────────────────────────────────┤
│ PK  id              UUID            │
│     title           VARCHAR(255)    │
│     description     TEXT            │ NULLABLE
│     priority        ENUM            │ low/medium/high
│     status          ENUM            │ pending/in-progress/completed
│     created_at      TIMESTAMP       │
│     updated_at      TIMESTAMP       │
│ FK  user_id         UUID            │ → users(id) CASCADE
└─────────────────────────────────────┘
```

---

## Relationships

**Users → Tasks:** One-to-Many
- FK: `tasks.user_id` → `users.id`
- Cascade: `ON DELETE CASCADE`

---

## Indexes

```sql
-- Foreign key performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Query optimization (for filtering)
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

---

## Key Constraints

- ✅ **Primary Keys:** UUID on both tables
- ✅ **Foreign Key:** tasks.user_id → users.id (enforced)
- ✅ **Unique:** email
- ✅ **NOT NULL:** email, hashed_password, title, priority, status, user_id
- ✅ **Defaults:** priority=medium, status=pending, is_active=true
- ✅ **Cascade Delete:** User deletion removes all their tasks

---

## Common Queries

```sql
-- Get user's tasks with filters
SELECT * FROM tasks
WHERE user_id = $user_id
  AND status = $status         -- optional filter
  AND priority = $priority     -- optional filter
ORDER BY created_at DESC;

-- Search tasks
SELECT * FROM tasks
WHERE user_id = $user_id
  AND (title ILIKE $search OR description ILIKE $search);

-- User authentication
SELECT * FROM users WHERE email = $email;

-- Create task
INSERT INTO tasks (title, description, priority, status, user_id)
VALUES (...) RETURNING *;

-- Update task
UPDATE tasks
SET title = $title, status = $status, priority = $priority, updated_at = NOW()
WHERE id = $task_id AND user_id = $user_id;
```

**Security:** All queries filter by `user_id` to prevent unauthorized access.
