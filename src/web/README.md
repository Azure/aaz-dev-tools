# AAZ Dev Tools - Web Frontend

A React-based web application for managing Azure CLI command development workflows, built with TypeScript, Vite, and Material-UI.

## Overview

This frontend application provides a user interface for:

- Managing workspaces for Azure CLI command development
- Configuring client endpoints and authentication
- Editing command trees and configurations
- Working with TypeSpec-based command definitions

## Project Structure

```
src/
├── components/           # Reusable UI components
├── views/               # Page-level components and views
│   └── workspace/       # Workspace management views
├── services/            # API service layer
│   └── workspaceApi.ts  # Workspace API functions
├── typespec/           # TypeSpec integration utilities
├── __tests__/          # Test files
│   ├── api/            # API layer tests
│   ├── components/     # Component unit tests
│   ├── integration/    # Integration tests
│   └── mocks/          # MSW mock handlers
├── App.tsx             # Main application component
├── theme.tsx           # Material-UI theme configuration
└── index.tsx          # Application entry point
```

## Technology Stack

- **React 18** with TypeScript
- **Vite** for build tooling and dev server
- **Material-UI (MUI)** for component library
- **Vitest** for testing framework
- **MSW (Mock Service Worker)** for API mocking
- **React Testing Library** for component testing
- **Axios** for HTTP requests

## Development

### Prerequisites

- Node.js 18.x or 20.x
- pnpm 9.5.0+

### Getting Started

1. **Install dependencies:**

   ```bash
   pnpm install
   ```

2. **Build TypeSpec and Web components:**

   ```bash
   pnpm run build:typespec
   pnpm run build:web
   ```

3. **Start development server:**

   ```bash
   pnpm dev
   ```

   Opens [http://localhost:3000](http://localhost:3000) with hot reload.

4. **Build for production:**

   ```bash
   pnpm build
   ```

   Builds to `dist/` folder with TypeScript compilation and optimized bundles.

5. **Preview production build:**
   ```bash
   pnpm preview
   ```

### Code Quality

- **Linting:**
  ```bash
  pnpm lint
  ```
  Runs ESLint with TypeScript rules and React-specific checks.

## Testing

This project uses **Vitest** as the testing framework with comprehensive test coverage.

### Running Tests

#### Basic Test Execution

```bash
# Run all tests once
pnpm test

# Run tests in watch mode (re-runs on file changes)
pnpm test:watch
```

#### Interactive Test UI

```bash
# Launch Vitest UI in browser - great for debugging and exploring tests
pnpm test:ui
```

Opens an interactive web interface showing:

- Test file explorer
- Real-time test results
- Coverage reports
- Test debugging tools

#### Coverage Reports

```bash
# Run tests with coverage analysis
pnpm test:coverage
```

Generates coverage reports in `coverage/` directory.

### Test Structure

- **Unit Tests** (`__tests__/components/`): Test individual React components
- **API Tests** (`__tests__/api/`): Test service layer and API integration
- **Integration Tests** (`__tests__/integration/`): Test component interaction flows
- **Mocks** (`__tests__/mocks/`): MSW handlers for API mocking

### Test Configuration

- **Environment**: `happy-dom` for fast DOM simulation
- **Setup**: `src/test-setup.ts` configures testing environment
- **Mocking**: MSW intercepts HTTP requests for consistent testing
- **Assertions**: Extended matchers from `@testing-library/jest-dom`

## Configuration

### Backend Integration

The app connects to a Python backend service. Configure the base URL in:

- Development: `vite.config.js` proxy settings
- Tests: `src/test-setup.ts` axios defaults

### Environment Variables

Create `.env.local` for local development overrides:

```bash
VITE_API_BASE_URL=http://localhost:5000
```

## Build & Deployment

1. **Production build:**

   ```bash
   pnpm build
   ```

2. **Build outputs:**

   - `dist/` - Optimized static files ready for deployment
   - TypeScript compilation ensures type safety
   - Vite optimizes bundles for performance

3. **Deployment:**
   - Serve `dist/` folder as static files
   - Configure proxy for API requests to backend service

## Development Workflow

1. **Feature development**: Use `pnpm dev` with hot reload
2. **Test as you go**: Use `pnpm test:watch` for immediate feedback
3. **Debug tests**: Use `pnpm test:ui` for visual test debugging
4. **Code quality**: Run `pnpm lint` before commits
5. **Build verification**: Run `pnpm build` to ensure production readiness

## API Integration

The frontend communicates with the AAZ Dev Tools Python backend through:

- REST API endpoints for workspace management
- Client configuration management
- Command tree operations
- TypeSpec integration workflows

See `src/services/workspaceApi.ts` for available API functions.

---

For questions about the broader AAZ Dev Tools project, see the main repository README.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
