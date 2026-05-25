import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { logger } from '../utils/logger';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ error, errorInfo });
    logger.error('ErrorBoundary caught error', {
      message: error.message,
      stack: error.stack,
      componentStack: (errorInfo as unknown as { componentStack: string }).componentStack,
    } as unknown as Error);
  }

  handleReload = (): void => {
    window.location.reload();
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  handleExportLogs = (): void => {
    const logs = logger.exportLogs();
    const blob = new Blob([logs], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `error-logs-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex items-center justify-center p-4">
        <div className="max-w-lg w-full bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-xl p-8 text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
            <AlertTriangle className="w-10 h-10 text-rose-500" />
          </div>

          <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">
            出现了一些问题
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mb-6">
            应用遇到了意外错误。请尝试刷新页面，或导出日志以便排查。
          </p>

          {this.state.error && (
            <div className="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-4 mb-6 text-left overflow-auto max-h-40">
              <p className="text-sm font-mono text-rose-600 dark:text-rose-400">
                {this.state.error.message}
              </p>
              {this.state.error.stack && (
                <details className="mt-2">
                  <summary className="text-xs text-zinc-500 dark:text-zinc-400 cursor-pointer">
                    查看详细错误
                  </summary>
                  <pre className="text-xs text-zinc-600 dark:text-zinc-300 mt-2 whitespace-pre-wrap">
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={this.handleReload}
              className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-sky-500 to-cyan-500 text-white font-semibold rounded-xl shadow-lg shadow-sky-500/25 hover:shadow-xl hover:shadow-sky-500/30 transition-all duration-300"
            >
              <RefreshCw className="w-5 h-5" />
              刷新页面
            </button>
            <button
              onClick={this.handleGoHome}
              className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
            >
              <Home className="w-5 h-5" />
              返回首页
            </button>
          </div>

          <button
            onClick={this.handleExportLogs}
            className="mt-4 text-sm text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
          >
            导出错误日志
          </button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
