---
goal: Implement admin user management dashboard
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, admin, user-management, rbac]
---

# Phase 11: Admin - User Management

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement the admin user management dashboard for viewing, creating, editing, and managing platform users with role assignment capabilities.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: User list with search, filter, pagination
- **REQ-002**: User CRUD operations
- **REQ-003**: Role assignment (Admin, User, Broker)
- **REQ-004**: User activation/deactivation

### Security Requirements

- **SEC-001**: Only Admin role can access
- **SEC-002**: Audit trail for admin actions
- **SEC-003**: Cannot deactivate own account

### Constraints

- **CON-001**: Admin routes require Admin role
- **CON-002**: User impersonation requires additional permission
- **CON-003**: Bulk actions have confirmation dialogs

---

## 2. Implementation Tasks

### GOAL-011: Implement admin user management dashboard

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-125 | Create `app/(admin)/admin/users/page.tsx` with user list | | |
| TASK-126 | Create `components/admin/UserTable.tsx` with search, filter, pagination | | |
| TASK-127 | Create `app/(admin)/admin/users/new/page.tsx` for user creation | | |
| TASK-128 | Create `components/admin/UserForm.tsx` with role assignment | | |
| TASK-129 | Create `app/(admin)/admin/users/[id]/page.tsx` for user details | | |
| TASK-130 | Create `components/admin/UserDetail.tsx` with strategy count, activity | | |
| TASK-131 | Implement user role modification (Admin/User/Broker) | | |
| TASK-132 | Implement user activation/deactivation toggle | | |
| TASK-133 | Add user impersonation for support (view as user) | | |
| TASK-134 | Create user activity log view | | |
| TASK-135 | Add bulk user actions (export, deactivate) | | |
| TASK-136 | Create user deletion with data handling confirmation | | |

---

## 3. Dependencies

- **DEP-001**: Shadcn/ui DataTable, Form, Dialog components
- **DEP-002**: Admin API endpoints
- **DEP-003**: Role-based middleware from Phase 3

---

## 4. Files

### Admin User Pages

- **FILE-001**: `admin-web/app/(admin)/admin/users/page.tsx` - User list
- **FILE-002**: `admin-web/app/(admin)/admin/users/new/page.tsx` - Create user
- **FILE-003**: `admin-web/app/(admin)/admin/users/[id]/page.tsx` - User detail
- **FILE-004**: `admin-web/app/(admin)/admin/users/[id]/edit/page.tsx` - Edit user
- **FILE-005**: `admin-web/app/(admin)/admin/users/loading.tsx` - Loading state

### Admin User Components

- **FILE-006**: `admin-web/components/admin/UserTable.tsx` - User data table
- **FILE-007**: `admin-web/components/admin/UserForm.tsx` - User create/edit form
- **FILE-008**: `admin-web/components/admin/UserDetail.tsx` - User detail view
- **FILE-009**: `admin-web/components/admin/UserFilters.tsx` - Filter controls
- **FILE-010**: `admin-web/components/admin/RoleSelect.tsx` - Role dropdown
- **FILE-011**: `admin-web/components/admin/UserActions.tsx` - Action menu
- **FILE-012**: `admin-web/components/admin/UserActivityLog.tsx` - Activity history
- **FILE-013**: `admin-web/components/admin/ImpersonateButton.tsx` - Impersonation
- **FILE-014**: `admin-web/components/admin/BulkActions.tsx` - Bulk operations
- **FILE-015**: `admin-web/components/admin/DeleteUserDialog.tsx` - Delete confirm

---

## User Table Columns

| Column | Description | Sortable | Filterable |
|--------|-------------|----------|------------|
| Name | User full name | Yes | Search |
| Email | User email | Yes | Search |
| Role | Admin/User/Broker | No | Dropdown |
| Status | Active/Inactive | No | Dropdown |
| Strategies | Count of strategies | Yes | No |
| Created | Registration date | Yes | Date range |
| Last Active | Last login | Yes | No |
| Actions | Edit, Impersonate, Deactivate, Delete | No | No |

---

## Success Criteria

✅ Phase 11 is complete when:

- [ ] User list with search and filters
- [ ] Pagination working correctly
- [ ] User creation form with role assignment
- [ ] User detail page with activity
- [ ] Role modification functionality
- [ ] Activation/deactivation toggle
- [ ] User impersonation for support
- [ ] User activity log view
- [ ] Bulk actions (export, deactivate)
- [ ] User deletion with confirmation

---

## Next Phase

[Phase 12: Admin - Strategy Oversight →](./phase-12-admin-strategies.md)
