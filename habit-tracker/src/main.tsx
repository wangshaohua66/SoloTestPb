import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import { logger } from './utils/logger';

const rootElement = document.getElementById('root');

if (!rootElement) {
  logger.error('Root element not found');
  throw new Error('Root element not found');
}

window.addEventListener('error', (event) => {
  logger.error('Uncaught error', {
    message: (event as unknown as { error: Error }).error?.message,
    stack: (event as unknown as { error: Error }).error?.stack,
    filename: (event as unknown as { filename: string }).filename,
    lineno: (event as unknown as { lineno: number }).lineno,
    colno: (event as unknown as { colno: number }).colno,
  } as unknown as Error);
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled promise rejection', {
    reason: (event as unknown as { reason: Error }).reason?.toString(),
    stack: (event as unknown as { reason: Error }).reason?.stack,
  } as unknown as Error);
});

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
