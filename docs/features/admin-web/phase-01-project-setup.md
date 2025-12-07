---
goal: Initialize Next.js 16 project with TypeScript and configure development environment
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, typescript, setup, shadcn, tailwind]
---

# Phase 1: Project Setup & Configuration

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Initialize the Next.js 16 admin web application with TypeScript, Tailwind CSS, Shadcn/ui, and all core dependencies for the Algo Trading System.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Next.js 16 with App Router architecture
- **REQ-002**: TypeScript strict mode enabled throughout
- **REQ-003**: Tailwind CSS for styling
- **REQ-004**: Shadcn/ui component library

### Patterns

- **PAT-001**: App Router directory structure
- **PAT-002**: Path aliases for imports (@/components, @/lib)
- **PAT-003**: Environment-based configuration

### Constraints

- **CON-001**: Node.js 18+ required
- **CON-002**: pnpm or npm as package manager
- **CON-003**: Backend API must be available at `ALGO_TRADING_CORE_URL`

---

## 2. Implementation Tasks

### GOAL-001: Initialize Next.js 16 project with TypeScript and configure development environment

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create Next.js 16 project with `npx create-next-app@latest admin-web --typescript --tailwind --eslint --app` | | |
| TASK-002 | Configure `tsconfig.json` with strict mode, path aliases (@/components, @/lib, @/hooks) | | |
| TASK-003 | Install and configure Shadcn/ui: `npx shadcn-ui@latest init` with New York style | | |
| TASK-004 | Install core dependencies: `zustand`, `react-hook-form`, `zod`, `@hookform/resolvers` | | |
| TASK-005 | Install NextAuth.js v5: `npm install next-auth@beta` | | |
| TASK-006 | Install charting library: `npm install recharts` | | |
| TASK-007 | Create `.env.local` with environment variables: NEXTAUTH_SECRET, NEXTAUTH_URL, ALGO_TRADING_CORE_URL | | |
| TASK-008 | Configure `tailwind.config.ts` with custom color scheme matching brand | | |
| TASK-009 | Create `lib/utils.ts` with utility functions (cn for class merging) | | |
| TASK-010 | Set up ESLint and Prettier configuration for code consistency | | |
| TASK-011 | Create project folder structure following App Router conventions | | |
| TASK-012 | Add `components.json` for Shadcn/ui component generation | | |

---

## 3. Dependencies

- **DEP-001**: Node.js 18+
- **DEP-002**: Next.js 16 with App Router
- **DEP-003**: TypeScript 5.x
- **DEP-004**: React 19
- **DEP-005**: Tailwind CSS 3.x
- **DEP-006**: Shadcn/ui component library
- **DEP-007**: Zustand for state management
- **DEP-008**: React Hook Form for form handling
- **DEP-009**: Zod for validation
- **DEP-010**: Recharts for data visualization
- **DEP-011**: Lucide React for icons

---

## 4. Files

### Configuration Files

- **FILE-001**: `admin-web/package.json` - Dependencies and scripts
- **FILE-002**: `admin-web/tsconfig.json` - TypeScript configuration with path aliases
- **FILE-003**: `admin-web/tailwind.config.ts` - Tailwind CSS configuration
- **FILE-004**: `admin-web/next.config.js` - Next.js configuration
- **FILE-005**: `admin-web/components.json` - Shadcn/ui configuration
- **FILE-006**: `admin-web/.env.local` - Environment variables (gitignored)
- **FILE-007**: `admin-web/.env.example` - Environment template
- **FILE-008**: `admin-web/.eslintrc.json` - ESLint configuration
- **FILE-009**: `admin-web/.prettierrc` - Prettier configuration

### Utility Files

- **FILE-010**: `admin-web/lib/utils.ts` - Utility functions (cn helper)

### Directory Structure

```text
admin-web/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── (auth)/
│   ├── (dashboard)/
│   └── (admin)/
├── components/
│   ├── ui/
│   ├── layout/
│   ├── auth/
│   ├── dashboard/
│   ├── strategies/
│   ├── brokers/
│   ├── playground/
│   └── admin/
├── lib/
│   ├── api/
│   ├── auth.ts
│   └── utils.ts
├── hooks/
├── store/
├── types/
└── config/
```

---

## Success Criteria

✅ Phase 1 is complete when:

- [ ] Next.js 16 project created with App Router
- [ ] TypeScript strict mode configured
- [ ] Shadcn/ui initialized with New York style
- [ ] All core dependencies installed
- [ ] Environment variables configured
- [ ] Folder structure created
- [ ] Development server runs successfully
- [ ] ESLint and Prettier working

---

## Next Phase

[Phase 2: Authentication System →](./phase-02-authentication.md)
